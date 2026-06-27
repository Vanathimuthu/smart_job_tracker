import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

const tabs = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'applications', label: 'Applications' },
  { id: 'resumes', label: 'Resumes' },
  { id: 'jobs', label: 'Jobs' },
  { id: 'interviews', label: 'Interviews' },
  { id: 'ai', label: 'AI tools' },
];

const defaultSummary = {
  applications_count: 0,
  applications_sent: 0,
  interviews_scheduled: 0,
  offers: 0,
  rejections: 0,
  average_ats_score: 0,
  jobs_count: 0,
  resumes_count: 0,
  interviews_count: 0,
};

const initialRegister = {
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  password: '',
  confirm_password: '',
};

const initialApplication = {
  company: '',
  role: '',
  location: '',
  salary: '',
  status: 'applied',
  job_description: '',
  job_url: '',
  apply_link: '',
  interview_date: '',
  interview_reminder_date: '',
  notes: '',
  company_notes: '',
};

const initialJob = {
  company: '',
  title: '',
  role: '',
  location: '',
  salary: '',
  description: '',
  job_url: '',
  apply_link: '',
  source: '',
};

const initialResume = {
  title: '',
  target_role: '',
  skills: '',
  content: '',
  ats_score: 0,
  is_default: false,
};

const initialInterview = {
  company: '',
  role: '',
  scheduled_at: '',
  platform: '',
  meeting_link: '',
  interviewer: '',
  notes: '',
};

const initialAi = {
  resume_text: '',
  job_description: '',
  section_text: '',
  target_role: '',
  company: '',
  skills: '',
  question: '',
};

const requiredFields = {
  login: [
    { key: 'username', label: 'Username' },
    { key: 'password', label: 'Password' },
  ],
  register: [
    { key: 'first_name', label: 'First name' },
    { key: 'username', label: 'Username' },
    { key: 'email', label: 'Email' },
    { key: 'phone_number', label: 'Phone' },
    { key: 'password', label: 'Password' },
    { key: 'confirm_password', label: 'Confirm password' },
  ],
  '/applications/': [
    { key: 'company', label: 'Company' },
    { key: 'role', label: 'Role' },
  ],
  '/resumes/': [
    { key: 'title', label: 'Title' },
  ],
  '/jobs/': [
    { key: 'company', label: 'Company' },
    { key: 'title', label: 'Title' },
  ],
  '/interviews/': [
    { key: 'company', label: 'Company' },
    { key: 'role', label: 'Role' },
  ],
};

function normalizeList(data) {
  return data?.results || data || [];
}

function formatApiError(error) {
  const data = error?.response?.data;
  if (!data) return 'Could not save this item.';
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;

  return Object.entries(data)
    .map(([field, value]) => {
      const message = Array.isArray(value) ? value.join(', ') : String(value);
      return `${field.replaceAll('_', ' ')}: ${message}`;
    })
    .join(' ');
}

function normalizeOptionalUrl(value) {
  const trimmed = String(value || '').trim();
  if (!trimmed) return '';

  const candidate = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
  try {
    const parsed = new URL(candidate);
    const validProtocol = parsed.protocol === 'http:' || parsed.protocol === 'https:';
    const validHost = parsed.hostname === 'localhost' || parsed.hostname.includes('.');
    return validProtocol && validHost ? parsed.href : '';
  } catch (error) {
    return '';
  }
}

function cleanPayload(payload) {
  const nullableDateFields = new Set(['interview_date', 'interview_reminder_date', 'scheduled_at']);
  const optionalUrlFields = new Set(['job_url', 'apply_link', 'meeting_link']);

  return Object.entries(payload).reduce((cleaned, [key, value]) => {
    if (nullableDateFields.has(key) && !value) return cleaned;
    if (optionalUrlFields.has(key)) {
      cleaned[key] = normalizeOptionalUrl(value);
      return cleaned;
    }
    cleaned[key] = value;
    return cleaned;
  }, {});
}

function isUnauthorized(error) {
  return error?.response?.status === 401;
}

function isAiQuotaError(error) {
  return error?.response?.status === 429;
}

function hasText(value) {
  return String(value || '').trim().length > 0;
}

function getMissingFields(payload, fields) {
  return fields
    .filter(({ key }) => !hasText(payload[key]))
    .map(({ label }) => label);
}

function toDateOnly(dateValue) {
  if (!dateValue) return null;
  const date = new Date(`${dateValue}T00:00:00`);
  if (Number.isNaN(date.getTime())) return null;
  date.setHours(0, 0, 0, 0);
  return date;
}

function getCurrentDateTimeLocal() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

function getApplicationReminder(app) {
  const reminderDate = toDateOnly(app.interview_reminder_date);
  if (!reminderDate) return null;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diffDays = Math.round((reminderDate - today) / 86400000);

  return {
    ...app,
    diffDays,
    reminderLabel: diffDays < 0 ? 'Overdue reminder' : diffDays === 0 ? 'Due today' : `Due in ${diffDays} day${diffDays === 1 ? '' : 's'}`,
  };
}

function formatDateTimeIST(dateString) {
  if (!dateString) return 'Date not set';
  try {
    const date = new Date(dateString);
    if (Number.isNaN(date.getTime())) return 'Invalid date';
    
    // Format with Asia/Kolkata timezone
    return new Intl.DateTimeFormat('en-IN', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZone: 'Asia/Kolkata'
    }).format(date);
  } catch (error) {
    return 'Invalid date';
  }
}

function getUpcomingInterviews(interviews) {
  if (!interviews.length) return [];
  
  const now = new Date();
  return interviews
    .map(interview => ({
      ...interview,
      scheduledDate: interview.scheduled_at ? new Date(interview.scheduled_at) : null,
      minutesUntil: interview.scheduled_at ? Math.round((new Date(interview.scheduled_at) - now) / 60000) : null,
    }))
    .filter(interview => interview.scheduledDate && interview.scheduledDate > now)
    .sort((a, b) => a.scheduledDate - b.scheduledDate);
}

function getDueInterviews(interviews) {
  if (!interviews.length) return [];
  
  const now = new Date();
  const twoHoursFromNow = new Date(now.getTime() + 2 * 60 * 60 * 1000);
  
  return interviews
    .map(interview => ({
      ...interview,
      scheduledDate: interview.scheduled_at ? new Date(interview.scheduled_at) : null,
      minutesUntil: interview.scheduled_at ? Math.round((new Date(interview.scheduled_at) - now) / 60000) : null,
    }))
    .filter(interview => interview.scheduledDate && interview.scheduledDate <= twoHoursFromNow && interview.scheduledDate > now)
    .sort((a, b) => a.scheduledDate - b.scheduledDate);
}

function Field({ label, required = false, children }) {
  return (
    <label className="block text-sm font-semibold text-white">
      <span>
        {label}
        {required ? <span className="ml-1 text-red-400" aria-label="required">*</span> : null}
      </span>
      {children}
    </label>
  );
}

function TextInput(props) {
  return (
    <input
      {...props}
      className="mt-2 w-full rounded-lg border border-purple-500/30 bg-black/40 backdrop-blur-sm px-3 py-2.5 text-sm text-white outline-none transition focus:border-purple-500 focus:ring-4 focus:ring-purple-500/30 placeholder-slate-400"
    />
  );
}

function TextArea(props) {
  return (
    <textarea
      {...props}
      className="mt-2 min-h-28 w-full resize-y rounded-lg border border-purple-500/30 bg-black/40 backdrop-blur-sm px-3 py-2.5 text-sm text-white outline-none transition focus:border-purple-500 focus:ring-4 focus:ring-purple-500/30 placeholder-slate-400"
    />
  );
}

function Select(props) {
  return (
    <select
      {...props}
      className="mt-2 w-full rounded-lg border border-purple-500/30 bg-black/40 backdrop-blur-sm px-3 py-2.5 text-sm text-white outline-none transition focus:border-purple-500 focus:ring-4 focus:ring-purple-500/30"
    />
  );
}

function PrimaryButton({ children, className = '', ...props }) {
  return (
    <button
      {...props}
      className={`inline-flex min-h-11 items-center justify-center rounded-lg bg-gradient-to-r from-purple-600 to-purple-700 px-4 py-2 text-sm font-bold text-white shadow-lg shadow-purple-500/50 transition hover:from-purple-500 hover:to-purple-600 disabled:cursor-not-allowed disabled:from-slate-500 disabled:to-slate-600 ${className}`}
    >
      {children}
    </button>
  );
}

function GhostButton({ children, className = '', ...props }) {
  return (
    <button
      {...props}
      className={`inline-flex min-h-10 items-center justify-center rounded-lg border border-purple-500/50 bg-black/30 backdrop-blur-sm px-4 py-2 text-sm font-bold text-purple-300 transition hover:border-purple-500 hover:bg-black/50 ${className}`}
    >
      {children}
    </button>
  );
}

function StatusPill({ value }) {
  const styles = {
    applied: 'bg-cyan-500/30 text-cyan-300',
    interview: 'bg-purple-500/30 text-purple-300',
    offered: 'bg-emerald-500/30 text-emerald-300',
    rejected: 'bg-red-500/30 text-red-300',
  };
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${styles[value] || styles.applied}`}>
      {value || 'saved'}
    </span>
  );
}

function ResultPanel({ title, data }) {
  if (!data) return null;

  return (
    <section className="rounded-xl border border-purple-500/40 bg-gradient-to-br from-black/60 via-purple-900/20 to-black/60 backdrop-blur-xl p-4 shadow-2xl card-shadow">
      <h3 className="text-lg font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">{title}</h3>
      <div className="mt-3 space-y-3 text-sm text-slate-100">
        {Object.entries(data).map(([key, value]) => (
          <div key={key}>
            <p className="font-bold capitalize text-cyan-300">{key.replaceAll('_', ' ')}</p>
            {Array.isArray(value) ? (
              <ul className="mt-1 flex flex-wrap gap-2">
                {value.map((item) => (
                  <li key={item} className="rounded-full bg-gradient-to-r from-cyan-500/30 to-purple-500/30 px-3 py-1 text-xs font-bold text-cyan-200 border border-cyan-500/50">
                    {item}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-1 whitespace-pre-wrap">{String(value)}</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [authMode, setAuthMode] = useState('login');
  const [login, setLogin] = useState({ username: '', password: '' });
  const [register, setRegister] = useState(initialRegister);
  const [summary, setSummary] = useState(defaultSummary);
  const [applications, setApplications] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [interviews, setInterviews] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [applicationForm, setApplicationForm] = useState(initialApplication);
  const [jobForm, setJobForm] = useState(initialJob);
  const [resumeForm, setResumeForm] = useState(initialResume);
  const [interviewForm, setInterviewForm] = useState(initialInterview);
  const [aiForm, setAiForm] = useState(initialAi);
  const [aiResult, setAiResult] = useState(null);
  const [aiBlocked, setAiBlocked] = useState(false);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const authHeaders = useMemo(() => (token ? { Authorization: `Bearer ${token}` } : {}), [token]);
  const applicationReminders = useMemo(
    () => applications
      .map(getApplicationReminder)
      .filter(Boolean)
      .sort((a, b) => a.diffDays - b.diffDays),
    [applications]
  );
  const dueApplicationReminders = useMemo(
    () => applicationReminders.filter((item) => item.diffDays <= 0),
    [applicationReminders]
  );
  const upcomingApplicationReminders = useMemo(
    () => applicationReminders.filter((item) => item.diffDays > 0 && item.diffDays <= 7),
    [applicationReminders]
  );

  const upcomingInterviews = useMemo(() => getUpcomingInterviews(interviews), [interviews]);
  const dueInterviews = useMemo(() => getDueInterviews(interviews), [interviews]);

  const clearSession = (sessionMessage = 'Session expired. Please log in again.') => {
    localStorage.removeItem('token');
    setToken('');
    setSummary(defaultSummary);
    setApplications([]);
    setJobs([]);
    setResumes([]);
    setInterviews([]);
    setNotifications([]);
    setMessage(sessionMessage);
  };

  const loadWorkspace = async () => {
    if (!token) return;
    try {
      const [summaryRes, appsRes, jobsRes, resumesRes, interviewsRes, notificationsRes] = await Promise.all([
        axios.get(`${API_BASE}/dashboard/summary/`, { headers: authHeaders }),
        axios.get(`${API_BASE}/applications/`, { headers: authHeaders }),
        axios.get(`${API_BASE}/jobs/`, { headers: authHeaders }),
        axios.get(`${API_BASE}/resumes/`, { headers: authHeaders }),
        axios.get(`${API_BASE}/interviews/`, { headers: authHeaders }),
        axios.get(`${API_BASE}/notifications/`, { headers: authHeaders }),
      ]);

      setSummary({ ...defaultSummary, ...summaryRes.data });
      setApplications(normalizeList(appsRes.data));
      setJobs(normalizeList(jobsRes.data));
      setResumes(normalizeList(resumesRes.data));
      setInterviews(normalizeList(interviewsRes.data));
      setNotifications(normalizeList(notificationsRes.data));
    } catch (error) {
      if (isUnauthorized(error)) {
        clearSession();
      } else {
        setMessage('Could not load the workspace. Please check that Django is running.');
      }
    }
  };

  useEffect(() => {
    loadWorkspace();
  }, [token]);

  useEffect(() => {
    if (!token || !dueApplicationReminders.length || !('Notification' in window)) return;

    const showDueNotifications = () => {
      dueApplicationReminders.forEach((app) => {
        const storageKey = `application-reminder-${app.id}-${app.interview_reminder_date}`;
        if (localStorage.getItem(storageKey)) return;

        new Notification(`Reminder: ${app.company}`, {
          body: `${app.role} is ${app.reminderLabel.toLowerCase()}.`,
        });
        localStorage.setItem(storageKey, 'shown');
      });
    };

    if (Notification.permission === 'granted') {
      showDueNotifications();
    } else if (Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        if (permission === 'granted') showDueNotifications();
      });
    }
  }, [token, dueApplicationReminders]);

  useEffect(() => {
    if (!token || !dueInterviews.length || !('Notification' in window)) return;

    const showInterviewReminders = () => {
      dueInterviews.forEach((interview) => {
        const storageKey = `interview-reminder-${interview.id}-${interview.scheduled_at}`;
        if (localStorage.getItem(storageKey)) return;

        const minutesUntil = Math.round((new Date(interview.scheduled_at) - new Date()) / 60000);
        const timeLabel = minutesUntil > 60 
          ? `in ${Math.round(minutesUntil / 60)} hour${Math.round(minutesUntil / 60) > 1 ? 's' : ''}`
          : `in ${minutesUntil} minute${minutesUntil > 1 ? 's' : ''}`;

        new Notification(`Interview Reminder: ${interview.company}`, {
          body: `Your interview for ${interview.role} is ${timeLabel}. ${interview.meeting_link ? 'Join link available.' : ''}`,
          tag: `interview-${interview.id}`,
          requireInteraction: true,
        });
        localStorage.setItem(storageKey, 'shown');
      });
    };

    if (Notification.permission === 'granted') {
      showInterviewReminders();
    } else if (Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        if (permission === 'granted') showInterviewReminders();
      });
    }
  }, [token, dueInterviews]);

  const submitAuth = async (event, mode) => {
    event.preventDefault();
    const payload = mode === 'register' ? register : login;
    const missingFields = getMissingFields(payload, requiredFields[mode]);
    if (missingFields.length) {
      showMessage(`Required fields: ${missingFields.join(', ')}`, 4000);
      return;
    }

    setBusy(true);
    setMessage('');
    try {
      if (mode === 'register') {
        await axios.post(`${API_BASE}/register/`, register);
        setRegister(initialRegister);
        setAuthMode('login');
        showMessage('Account created. Log in with your new credentials.', 4000);
      } else {
        const response = await axios.post(`${API_BASE}/login/`, login);
        localStorage.setItem('token', response.data.access);
        setToken(response.data.access);
        showMessage('Logged in successfully.', 2000);
      }
    } catch (error) {
      showMessage(mode === 'register' ? 'Registration failed. Check all fields.' : 'Login failed.', 4000);
    } finally {
      setBusy(false);
    }
  };

  const postResource = async (event, url, payload, resetForm) => {
    event.preventDefault();
    const missingFields = getMissingFields(payload, requiredFields[url] || []);
    if (missingFields.length) {
      showMessage(`Required fields: ${missingFields.join(', ')}`, 4000);
      return;
    }

    setBusy(true);
    setMessage('');
    try {
      await axios.post(`${API_BASE}${url}`, cleanPayload(payload), { headers: authHeaders });
      resetForm();
      await loadWorkspace();
      showMessage('Saved successfully.', 3000);
    } catch (error) {
      if (isUnauthorized(error)) {
        clearSession();
      } else {
        showMessage(formatApiError(error), 5000);
      }
    } finally {
      setBusy(false);
    }
  };

  const runAiTool = async (tool) => {
    if (aiBlocked) {
      setMessage('AI is paused because the OpenAI API key has insufficient quota. Add billing/credits or use another API key, then restart Django and refresh.');
      return;
    }

    setBusy(true);
    setMessage('');
    setAiResult(null);

    const payloads = {
      analyze: {
        url: '/ai/analyze/',
        payload: { resume_text: aiForm.resume_text, job_description: aiForm.job_description },
        title: 'ATS analysis',
      },
      match: {
        url: '/ai/match/',
        payload: { resume_text: aiForm.resume_text, job_description: aiForm.job_description },
        title: 'Resume match',
      },
      rewrite: {
        url: '/ai/rewrite/',
        payload: { section_text: aiForm.section_text, target_role: aiForm.target_role },
        title: 'Rewrite result',
      },
      interview: {
        url: '/ai/interview-prep/',
        payload: {
          job_description: aiForm.job_description,
          skills: aiForm.skills.split(',').map((skill) => skill.trim()).filter(Boolean),
        },
        title: 'Interview prep',
      },
      research: {
        url: '/ai/company-research/',
        payload: { company: aiForm.company, job_description: aiForm.job_description },
        title: 'Company research',
      },
      coach: {
        url: '/ai/career-coach/',
        payload: {
          question: aiForm.question,
          resume_text: aiForm.resume_text,
          job_description: aiForm.job_description,
        },
        title: 'Career coach',
      },
    };

    try {
      const config = payloads[tool];
      const validationMessages = {
        analyze: !hasText(aiForm.resume_text) || !hasText(aiForm.job_description)
          ? 'Add resume text and job description before running ATS scan.'
          : '',
        match: !hasText(aiForm.resume_text) || !hasText(aiForm.job_description)
          ? 'Add resume text and job description before matching the job.'
          : '',
        rewrite: !hasText(aiForm.section_text)
          ? 'Add the resume section you want to rewrite.'
          : '',
        interview: !hasText(aiForm.job_description) && !hasText(aiForm.skills)
          ? 'Add a job description or skills before generating interview prep.'
          : '',
        research: !hasText(aiForm.company)
          ? 'Add the company name before running company research.'
          : '',
        coach: !hasText(aiForm.question)
          ? 'Add your career question before asking the coach.'
          : '',
      };

      if (validationMessages[tool]) {
        setMessage(validationMessages[tool]);
        return;
      }

      const response = await axios.post(`${API_BASE}${config.url}`, config.payload);
      setAiResult({ title: config.title, data: response.data });
    } catch (error) {
      if (isAiQuotaError(error)) {
        setAiBlocked(true);
      }
      setMessage(formatApiError(error) || 'AI tool could not complete. Please add the required text and try again.');
    } finally {
      setBusy(false);
    }
  };

  const logout = () => {
    clearSession('Logged out.');
  };

  const showMessage = (text, duration = 3500) => {
    setMessage(text);
    if (text && duration > 0) {
      setTimeout(() => setMessage(''), duration);
    }
  };

  if (!token) {
    return (
      <main className="app-shell min-h-screen px-4 py-8 text-white">
        <section className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="flex min-h-[80vh] flex-col justify-center">
            <p className="text-sm font-black uppercase tracking-[0.24em] bg-gradient-to-r from-cyan-300 via-purple-300 to-orange-300 bg-clip-text text-transparent">Smart resume workspace</p>
            <h1 className="mt-4 max-w-2xl text-4xl font-black leading-tight text-white sm:text-6xl">
              Track jobs, tune resumes, and prepare for interviews in one vibrant workspace.
            </h1>
            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-200">
              A light blue and pink job search command center with ATS analysis, resume rewrites,
              job matching, company research, interview prep, reminders, and application tracking.
            </p>
            <div className="mt-8 grid max-w-2xl gap-3 sm:grid-cols-3">
              {['ATS scoring', 'Job tracker', 'AI prep'].map((item) => (
                <div key={item} className="rounded-lg border border-purple-500/50 bg-black/40 backdrop-blur-sm px-4 py-3 text-sm font-bold text-cyan-300 shadow-lg">
                  {item}
                </div>
              ))}
            </div>
          </div>

          <div className="grid content-center gap-4">
            {message ? <div className="fixed top-4 right-4 z-50 max-w-sm rounded-lg bg-gradient-to-r from-pink-500 to-pink-600 px-4 py-3 text-sm font-bold text-white shadow-lg">{message}</div> : null}

            {authMode === 'login' ? (
              <form noValidate onSubmit={(event) => submitAuth(event, 'login')} className="rounded-lg border border-purple-500/50 bg-black/50 backdrop-blur-md p-5 shadow-2xl">
                <h2 className="text-xl font-black text-white">Login</h2>
                <div className="mt-4 grid gap-3">
                  <Field label="Username" required>
                    <TextInput value={login.username} onChange={(e) => setLogin({ ...login, username: e.target.value })} required />
                  </Field>
                  <Field label="Password" required>
                    <TextInput type="password" value={login.password} onChange={(e) => setLogin({ ...login, password: e.target.value })} required />
                  </Field>
                  <PrimaryButton disabled={busy}>Login</PrimaryButton>
                </div>
                <p className="mt-4 text-center text-sm font-semibold text-slate-200">
                  Don't have an account?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('register');
                      setMessage('');
                    }}
                    className="font-black text-cyan-300 underline-offset-4 hover:text-pink-300 hover:underline"
                  >
                    Create account
                  </button>
                </p>
              </form>
            ) : (
              <form noValidate onSubmit={(event) => submitAuth(event, 'register')} className="rounded-lg border border-purple-500/50 bg-black/50 backdrop-blur-md p-5 shadow-2xl">
                <h2 className="text-xl font-black text-white">Create account</h2>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <Field label="First name" required>
                    <TextInput value={register.first_name} onChange={(e) => setRegister({ ...register, first_name: e.target.value })} required />
                  </Field>
                  <Field label="Last name">
                    <TextInput value={register.last_name} onChange={(e) => setRegister({ ...register, last_name: e.target.value })} />
                  </Field>
                  <Field label="Username" required>
                    <TextInput value={register.username} onChange={(e) => setRegister({ ...register, username: e.target.value })} required />
                  </Field>
                  <Field label="Email" required>
                    <TextInput type="email" value={register.email} onChange={(e) => setRegister({ ...register, email: e.target.value })} required />
                  </Field>
                  <Field label="Phone" required>
                    <TextInput value={register.phone_number} onChange={(e) => setRegister({ ...register, phone_number: e.target.value })} required />
                  </Field>
                  <Field label="Password" required>
                    <TextInput type="password" value={register.password} onChange={(e) => setRegister({ ...register, password: e.target.value })} required />
                  </Field>
                  <Field label="Confirm password" required>
                    <TextInput type="password" value={register.confirm_password} onChange={(e) => setRegister({ ...register, confirm_password: e.target.value })} required />
                  </Field>
                  <PrimaryButton disabled={busy} className="sm:mt-7">Register</PrimaryButton>
                </div>
                <p className="mt-4 text-center text-sm font-semibold text-slate-200">
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setMessage('');
                    }}
                    className="font-black text-cyan-300 underline-offset-4 hover:text-pink-300 hover:underline"
                  >
                    Login
                  </button>
                </p>
              </form>
            )}
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell app-theme-dark min-h-screen text-white">
      <header className="app-header sticky top-0 z-20 border-b border-purple-500/30 bg-black/40 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.2em] text-purple-400">Smart Resume Tools</p>
            <h1 className="text-4xl font-black bg-gradient-to-r from-cyan-300 via-purple-400 to-orange-400 bg-clip-text text-transparent">Smart Job Tracker</h1>
          </div>
          <nav className="flex gap-2 overflow-x-auto pb-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`shrink-0 rounded-lg px-4 py-2.5 text-sm font-bold transition backdrop-blur-sm ${
                  activeTab === tab.id ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg shadow-purple-500/50 border border-purple-500/50' : 'bg-slate-800/50 text-slate-300 hover:bg-slate-700/50 border border-slate-700/50'
                }`}
              >
                {tab.label}
              </button>
            ))}
            <GhostButton onClick={logout}>Logout</GhostButton>
          </nav>
        </div>
      </header>

      <div className="relative z-10 mx-auto max-w-7xl px-4 py-6">
        {message ? <div className="fixed top-4 right-4 z-50 max-w-sm rounded-lg bg-gradient-to-r from-pink-500 to-pink-600 px-4 py-3 text-sm font-bold text-white shadow-lg">{message}</div> : null}

        {activeTab === 'dashboard' ? (
          <section className="grid gap-5">
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {[
                ['Applications', summary.applications_count],
                ['Interviews', summary.interviews_scheduled],
                ['Offers', summary.offers],
                ['Average ATS', `${summary.average_ats_score}%`],
                ['Saved jobs', summary.jobs_count],
                ['Resumes', summary.resumes_count],
                ['Rejections', summary.rejections],
                ['Reminders due', dueApplicationReminders.length],
              ].map(([label, value]) => (
                <article key={label} className="rounded-xl border border-purple-500/40 bg-gradient-to-br from-black/70 via-purple-900/20 to-black/70 backdrop-blur-xl p-5 shadow-2xl hover:shadow-purple-500/20">
                  <p className="text-xs font-bold uppercase tracking-wider text-purple-400">{label}</p>
                  <p className="mt-3 text-4xl font-black bg-gradient-to-r from-cyan-300 to-purple-400 bg-clip-text text-transparent">{value}</p>
                </article>
              ))}
            </div>
            <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
              <section className="rounded-xl border border-purple-500/40 bg-gradient-to-br from-black/60 via-purple-900/20 to-black/60 backdrop-blur-xl p-5 shadow-2xl">
                <h2 className="text-2xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-orange-300 bg-clip-text text-transparent">Pipeline</h2>
                <div className="mt-4 grid gap-3">
                  {applications.slice(0, 5).map((app) => (
                    <div key={app.id} className="flex flex-col gap-2 rounded-lg border border-purple-500/30 bg-gradient-to-r from-purple-500/15 to-cyan-500/10 backdrop-blur-sm p-3 sm:flex-row sm:items-center sm:justify-between hover:border-purple-500/50 transition-all">
                      <div>
                        <p className="font-bold text-lg text-cyan-300">{app.company}</p>
                        <p className="text-sm text-slate-200">{app.role}</p>
                      </div>
                      <StatusPill value={app.status} />
                    </div>
                  ))}
                  {!applications.length ? <p className="text-sm text-slate-400">No applications yet.</p> : null}
                </div>
              </section>
              <section className="rounded-xl border border-purple-500/40 bg-gradient-to-br from-black/60 via-purple-900/20 to-black/60 backdrop-blur-xl p-5 shadow-2xl">
                <h2 className="text-2xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Upcoming interviews</h2>
                <div className="mt-4 space-y-3">
                  {interviews.slice(0, 4).map((item) => (
                    <article key={item.id} className="rounded-lg border border-purple-500/30 bg-gradient-to-r from-purple-500/15 to-cyan-500/10 backdrop-blur-sm p-3 hover:border-purple-500/50 transition-all">
                      <p className="font-bold text-cyan-300">{item.company}</p>
                      <p className="text-sm text-slate-200">{item.role} {item.scheduled_at ? `- ${formatDateTimeIST(item.scheduled_at)}` : ''}</p>
                    </article>
                  ))}
                  {!interviews.length ? <p className="text-sm text-slate-400">No interviews scheduled.</p> : null}
                </div>
              </section>
            </div>
          </section>
        ) : null}

        {activeTab === 'applications' ? (
          <section className="grid gap-5">
            <form
              noValidate
              onSubmit={(event) => postResource(event, '/applications/', applicationForm, () => setApplicationForm(initialApplication))}
              className="self-start rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-5 shadow-lg"
            >
              <h2 className="text-lg font-black">Add application</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <Field label="Company" required><TextInput value={applicationForm.company} onChange={(e) => setApplicationForm({ ...applicationForm, company: e.target.value })} required /></Field>
                <Field label="Role" required><TextInput value={applicationForm.role} onChange={(e) => setApplicationForm({ ...applicationForm, role: e.target.value })} required /></Field>
                <Field label="Location"><TextInput value={applicationForm.location} onChange={(e) => setApplicationForm({ ...applicationForm, location: e.target.value })} /></Field>
                <Field label="Salary"><TextInput value={applicationForm.salary} onChange={(e) => setApplicationForm({ ...applicationForm, salary: e.target.value })} /></Field>
                <Field label="Status">
                  <Select value={applicationForm.status} onChange={(e) => setApplicationForm({ ...applicationForm, status: e.target.value })}>
                    <option value="applied">Applied</option>
                    <option value="interview">Interview</option>
                    <option value="offered">Offered</option>
                    <option value="rejected">Rejected</option>
                  </Select>
                </Field>
                <Field label="Reminder"><TextInput type="date" value={applicationForm.interview_reminder_date} onChange={(e) => setApplicationForm({ ...applicationForm, interview_reminder_date: e.target.value })} /></Field>
                <Field label="Apply link"><TextInput value={applicationForm.apply_link} onChange={(e) => setApplicationForm({ ...applicationForm, apply_link: e.target.value })} /></Field>
                <Field label="Job URL"><TextInput value={applicationForm.job_url} onChange={(e) => setApplicationForm({ ...applicationForm, job_url: e.target.value })} /></Field>
                <div className="sm:col-span-2"><Field label="Job description"><TextArea value={applicationForm.job_description} onChange={(e) => setApplicationForm({ ...applicationForm, job_description: e.target.value })} /></Field></div>
                <div className="sm:col-span-2"><Field label="Notes"><TextArea value={applicationForm.notes} onChange={(e) => setApplicationForm({ ...applicationForm, notes: e.target.value })} /></Field></div>
                <PrimaryButton disabled={busy} className="sm:col-span-2">Save application</PrimaryButton>
              </div>
            </form>
            <section className="grid gap-3 xl:grid-cols-2">
              {dueApplicationReminders.length || upcomingApplicationReminders.length ? (
                <div className="rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-4 shadow-lg xl:col-span-2">
                  <h3 className="text-xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Application reminders</h3>
                  <div className="mt-3 grid gap-2">
                    {[...dueApplicationReminders, ...upcomingApplicationReminders].slice(0, 5).map((app) => (
                      <div key={`${app.id}-${app.interview_reminder_date}`} className="flex flex-col gap-1 rounded-lg border border-purple-500/30 bg-gradient-to-r from-purple-500/20 to-cyan-500/10 backdrop-blur-sm px-3 py-2.5 sm:flex-row sm:items-center sm:justify-between hover:border-purple-500/50 transition-all">
                        <div>
                          <p className="font-bold text-lg bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">{app.company} - {app.role}</p>
                          <p className="text-sm text-slate-300">Reminder date: {app.interview_reminder_date}</p>
                        </div>
                        <span className="rounded-full bg-purple-500/30 px-3 py-1 text-xs font-bold text-purple-300">{app.reminderLabel}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
              {applications.map((app) => (
                <article key={app.id} className="rounded-xl border border-purple-500/40 bg-gradient-to-br from-black/70 via-purple-900/20 to-black/70 backdrop-blur-xl p-4 shadow-2xl hover:shadow-purple-500/20 transition-all">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-black bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">{app.company}</h3>
                      <p className="text-sm text-slate-200">{app.role} {app.location ? `- ${app.location}` : ''}</p>
                    </div>
                    <StatusPill value={app.status} />
                  </div>
                  <p className="mt-3 text-sm text-slate-300">{app.notes || app.company_notes || 'No notes added yet.'}</p>
                  {app.interview_reminder_date ? (
                    <p className="mt-2 text-sm font-bold text-pink-600">Reminder: {app.interview_reminder_date}</p>
                  ) : null}
                </article>
              ))}
            </section>
          </section>
        ) : null}

        {activeTab === 'resumes' ? (
          <section className="grid gap-5">
            <form noValidate onSubmit={(event) => postResource(event, '/resumes/', resumeForm, () => setResumeForm(initialResume))} className="self-start rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-5 shadow-lg">
              <h2 className="text-lg font-black">Resume vault</h2>
              <div className="mt-4 grid gap-3">
                <Field label="Title" required><TextInput value={resumeForm.title} onChange={(e) => setResumeForm({ ...resumeForm, title: e.target.value })} required /></Field>
                <Field label="Target role"><TextInput value={resumeForm.target_role} onChange={(e) => setResumeForm({ ...resumeForm, target_role: e.target.value })} /></Field>
                <Field label="Skills"><TextInput value={resumeForm.skills} onChange={(e) => setResumeForm({ ...resumeForm, skills: e.target.value })} /></Field>
                <Field label="Resume content"><TextArea value={resumeForm.content} onChange={(e) => setResumeForm({ ...resumeForm, content: e.target.value })} /></Field>
                <PrimaryButton disabled={busy}>Save resume</PrimaryButton>
              </div>
            </form>
            <section className="grid gap-3 xl:grid-cols-2">
              {resumes.map((resume) => (
                <article key={resume.id} className="rounded-xl border border-purple-500/40 bg-gradient-to-br from-black/70 via-purple-900/20 to-black/70 backdrop-blur-xl p-4 shadow-2xl hover:shadow-purple-500/20 transition-all">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-black text-lg bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">{resume.title}</h3>
                      <p className="text-sm text-slate-300">{resume.target_role || 'General resume'}</p>
                    </div>
                    <span className="rounded-full bg-gradient-to-r from-cyan-500/40 to-purple-500/40 px-3 py-1.5 text-xs font-bold text-cyan-300 border border-cyan-500/50">{resume.ats_score || 0}% ATS</span>
                  </div>
                  <p className="mt-3 line-clamp-3 text-sm text-slate-300">{resume.skills || resume.content || 'No content added.'}</p>
                </article>
              ))}
            </section>
          </section>
        ) : null}

        {activeTab === 'jobs' ? (
          <section className="grid gap-5">
            <form noValidate onSubmit={(event) => postResource(event, '/jobs/', jobForm, () => setJobForm(initialJob))} className="self-start rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-5 shadow-lg">
              <h2 className="text-lg font-black">Save job</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <Field label="Company" required><TextInput value={jobForm.company} onChange={(e) => setJobForm({ ...jobForm, company: e.target.value })} required /></Field>
                <Field label="Title" required><TextInput value={jobForm.title} onChange={(e) => setJobForm({ ...jobForm, title: e.target.value })} required /></Field>
                <Field label="Role"><TextInput value={jobForm.role} onChange={(e) => setJobForm({ ...jobForm, role: e.target.value })} /></Field>
                <Field label="Location"><TextInput value={jobForm.location} onChange={(e) => setJobForm({ ...jobForm, location: e.target.value })} /></Field>
                <Field label="Salary"><TextInput value={jobForm.salary} onChange={(e) => setJobForm({ ...jobForm, salary: e.target.value })} /></Field>
                <Field label="Source"><TextInput value={jobForm.source} onChange={(e) => setJobForm({ ...jobForm, source: e.target.value })} /></Field>
                <div className="sm:col-span-2"><Field label="Description"><TextArea value={jobForm.description} onChange={(e) => setJobForm({ ...jobForm, description: e.target.value })} /></Field></div>
                <PrimaryButton disabled={busy} className="sm:col-span-2">Save job</PrimaryButton>
              </div>
            </form>
            <section className="grid gap-3 xl:grid-cols-2">
              {jobs.map((job) => (
                <article key={job.id} className="rounded-xl border border-purple-500/40 bg-gradient-to-br from-black/70 via-purple-900/20 to-black/70 backdrop-blur-xl p-4 shadow-2xl hover:shadow-purple-500/20 transition-all">
                  <h3 className="font-black text-lg bg-gradient-to-r from-cyan-300 to-purple-300 bg-clip-text text-transparent">{job.company}</h3>
                  <p className="text-sm text-slate-200">{job.title || job.role} {job.location ? `- ${job.location}` : ''}</p>
                  <p className="mt-3 line-clamp-2 text-sm text-slate-200">{job.description || 'No description saved.'}</p>
                </article>
              ))}
            </section>
          </section>
        ) : null}

        {activeTab === 'interviews' ? (
          <section className="grid gap-5">
            <form noValidate onSubmit={(event) => postResource(event, '/interviews/', interviewForm, () => setInterviewForm(initialInterview))} className="self-start rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-5 shadow-lg">
              <h2 className="text-lg font-black">Schedule interview</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <Field label="Company" required><TextInput value={interviewForm.company} onChange={(e) => setInterviewForm({ ...interviewForm, company: e.target.value })} required /></Field>
                <Field label="Role" required><TextInput value={interviewForm.role} onChange={(e) => setInterviewForm({ ...interviewForm, role: e.target.value })} required /></Field>
                <Field label="Date and time">
                  <div className="mt-2 flex gap-2">
                    <TextInput type="datetime-local" value={interviewForm.scheduled_at} onChange={(e) => setInterviewForm({ ...interviewForm, scheduled_at: e.target.value })} className="flex-1" />
                    <GhostButton type="button" onClick={() => setInterviewForm({ ...interviewForm, scheduled_at: getCurrentDateTimeLocal() })} className="shrink-0">Now</GhostButton>
                  </div>
                </Field>
                <Field label="Platform"><TextInput value={interviewForm.platform} onChange={(e) => setInterviewForm({ ...interviewForm, platform: e.target.value })} /></Field>
                <Field label="Meeting link"><TextInput value={interviewForm.meeting_link} onChange={(e) => setInterviewForm({ ...interviewForm, meeting_link: e.target.value })} /></Field>
                <Field label="Interviewer"><TextInput value={interviewForm.interviewer} onChange={(e) => setInterviewForm({ ...interviewForm, interviewer: e.target.value })} /></Field>
                <div className="sm:col-span-2"><Field label="Notes"><TextArea value={interviewForm.notes} onChange={(e) => setInterviewForm({ ...interviewForm, notes: e.target.value })} /></Field></div>
                <PrimaryButton disabled={busy} className="sm:col-span-2">Save interview</PrimaryButton>
              </div>
            </form>
            <section className="grid gap-3 xl:grid-cols-2">
              {dueInterviews.length > 0 ? (
                <div className="rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-4 shadow-lg xl:col-span-2">
                  <h3 className="text-xl font-black bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Upcoming reminders</h3>
                  <div className="mt-3 grid gap-2">
                    {dueInterviews.map((interview) => (
                      <div key={`${interview.id}-${interview.scheduled_at}`} className="flex flex-col gap-1 rounded-lg border border-purple-500/30 bg-gradient-to-r from-purple-500/20 to-cyan-500/10 backdrop-blur-sm px-3 py-2.5 sm:flex-row sm:items-center sm:justify-between hover:border-purple-500/50 transition-all">
                        <div>
                          <p className="font-bold text-white">{interview.company} - {interview.role}</p>
                          <p className="text-sm text-slate-300">Scheduled: {formatDateTimeIST(interview.scheduled_at)}</p>
                        </div>
                        <span className="rounded-full bg-purple-500/30 px-3 py-1 text-xs font-bold text-purple-300">{interview.minutesUntil} min</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
              {interviews.map((item) => (
                <article key={item.id} className="rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-4 shadow-lg">
                  <h3 className="font-black">{item.company}</h3>
                  <p className="text-sm text-slate-300">{item.role}</p>
                  <p className="mt-2 text-sm font-bold text-pink-600">{formatDateTimeIST(item.scheduled_at)}</p>
                  <p className="mt-2 text-sm text-slate-300">{item.notes || item.platform || 'No details added.'}</p>
                </article>
              ))}
            </section>
          </section>
        ) : null}

        {activeTab === 'ai' ? (
          <section className="grid gap-5">
            <div className="self-start rounded-lg border border-purple-500/30 bg-black/50 backdrop-blur-sm p-5 shadow-lg">
              <h2 className="text-lg font-black">AI resume and career tools</h2>
              <div className="mt-4 grid gap-3">
                <Field label="Resume text"><TextArea value={aiForm.resume_text} onChange={(e) => setAiForm({ ...aiForm, resume_text: e.target.value })} /></Field>
                <Field label="Job description"><TextArea value={aiForm.job_description} onChange={(e) => setAiForm({ ...aiForm, job_description: e.target.value })} /></Field>
                <Field label="Resume section to rewrite"><TextArea value={aiForm.section_text} onChange={(e) => setAiForm({ ...aiForm, section_text: e.target.value })} /></Field>
                <div className="grid gap-3 sm:grid-cols-3">
                  <Field label="Target role"><TextInput value={aiForm.target_role} onChange={(e) => setAiForm({ ...aiForm, target_role: e.target.value })} /></Field>
                  <Field label="Company"><TextInput value={aiForm.company} onChange={(e) => setAiForm({ ...aiForm, company: e.target.value })} /></Field>
                  <Field label="Skills"><TextInput value={aiForm.skills} onChange={(e) => setAiForm({ ...aiForm, skills: e.target.value })} placeholder="Django, React" /></Field>
                </div>
                <Field label="Career question"><TextInput value={aiForm.question} onChange={(e) => setAiForm({ ...aiForm, question: e.target.value })} /></Field>
                <div className="grid gap-2 sm:grid-cols-3">
                  <PrimaryButton disabled={busy || aiBlocked} onClick={() => runAiTool('analyze')} type="button">ATS scan</PrimaryButton>
                  <PrimaryButton disabled={busy || aiBlocked} onClick={() => runAiTool('match')} type="button">Match job</PrimaryButton>
                  <PrimaryButton disabled={busy || aiBlocked} onClick={() => runAiTool('rewrite')} type="button">Rewrite</PrimaryButton>
                  <GhostButton disabled={busy || aiBlocked} onClick={() => runAiTool('interview')} type="button">Interview prep</GhostButton>
                  <GhostButton disabled={busy || aiBlocked} onClick={() => runAiTool('research')} type="button">Research</GhostButton>
                  <GhostButton disabled={busy || aiBlocked} onClick={() => runAiTool('coach')} type="button">Coach</GhostButton>
                </div>
                {aiBlocked ? (
                  <p className="rounded-lg border border-purple-500/30 bg-purple-500/10 px-3 py-2 text-sm font-bold text-purple-300">
                    AI is paused until the OpenAI project has quota. Update billing/API key, restart Django, then refresh this page.
                  </p>
                ) : null}
              </div>
            </div>
            <ResultPanel title={aiResult?.title || 'Results'} data={aiResult?.data} />
          </section>
        ) : null}
      </div>
    </main>
  );
}

export default App;
