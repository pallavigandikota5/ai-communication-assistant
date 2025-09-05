'use client';
import useSWR from 'swr';
import { useMemo, useState } from 'react';
import { ResponsiveContainer, PieChart, Pie, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const API = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
const fetcher = (url) => fetch(url).then(r => r.json());

export default function Home() {
  const { data: emails } = useSWR(`${API}/api/emails/`, fetcher, { refreshInterval: 5000 });
  const { data: stats } = useSWR(`${API}/api/stats/overview`, fetcher, { refreshInterval: 10000 });
  const [activeEmail, setActiveEmail] = useState(null);
  const [reply, setReply] = useState('');

  const sortedEmails = useMemo(() => {
    if (!emails) return [];
    return emails.slice().sort((a, b) => {
      if (a.priority !== b.priority) return a.priority === 'urgent' ? -1 : 1;
      return new Date(b.received_at) - new Date(a.received_at);
    });
  }, [emails]);

  const selectEmail = async (e) => {
    setActiveEmail(e);
    const draftRes = await fetch(`${API}/api/emails/${e.id}/draft`).then(r => r.json());
    setReply(draftRes?.draft || '');
  };

  const sendReply = async () => {
    if (!activeEmail) return;
    await fetch(`${API}/api/responses/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email_id: activeEmail.id,
        to: activeEmail.sender,
        subject: `Re: ${activeEmail.subject}`,
        body: reply
      })
    });
    alert('Sent!');
  };

  const resolve = async () => {
    if (!activeEmail) return;
    await fetch(`${API}/api/responses/${activeEmail.id}/resolve`, { method: 'POST' });
    alert('Marked resolved');
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16 }}>
      <div>
        <Panel title="Inbox (Filtered)">
          <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
            <Stat label="Total" value={stats?.total ?? '-'} />
            <Stat label="Last 24h" value={stats?.last24 ?? '-'} />
            <Stat label="Pending" value={stats?.pending ?? '-'} />
            <Stat label="Resolved" value={stats?.resolved ?? '-'} />
          </div>
          <div style={{ maxHeight: 520, overflow: 'auto', border: '1px solid #1d2a44', borderRadius: 12 }}>
            {sortedEmails.map(e => (
              <div key={e.id} onClick={() => selectEmail(e)} style={{ padding: 12, borderBottom: '1px solid #172038', cursor: 'pointer', background: activeEmail?.id === e.id ? '#111a2f' : 'transparent' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 600 }}>{e.subject}</div>
                  <Badge color={e.priority === 'urgent' ? '#ff6b6b' : '#3ecf8e'}>{e.priority}</Badge>
                </div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>{e.sender}</div>
                <div style={{ fontSize: 12, opacity: 0.6 }}>{new Date(e.received_at).toLocaleString()}</div>
                <div style={{ marginTop: 6, fontSize: 13, opacity: 0.9, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{e.summary || e.body}</div>
                <div style={{ marginTop: 6 }}>
                  <Badge color={e.sentiment === 'negative' ? '#ff6b6b' : e.sentiment === 'positive' ? '#3ecf8e' : '#8892b0'}>{e.sentiment}</Badge>
                  {e.phone && <Badge color="#8892b0">📞 {e.phone}</Badge>}
                  {e.alt_email && <Badge color="#8892b0">✉️ {e.alt_email}</Badge>}
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Analytics">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={{ background: '#0f1a33', padding: 12, borderRadius: 12 }}>
              <h3 style={{ marginTop: 0 }}>Sentiment</h3>
              {stats && (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: 'Positive', value: stats.sentiment.positive },
                    { name: 'Neutral', value: stats.sentiment.neutral },
                    { name: 'Negative', value: stats.sentiment.negative },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="value" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
            <div style={{ background: '#0f1a33', padding: 12, borderRadius: 12 }}>
              <h3 style={{ marginTop: 0 }}>Priority</h3>
              {stats && (
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={[
                      { name: 'Urgent', value: stats.priority.urgent },
                      { name: 'Not Urgent', value: stats.priority.not_urgent },
                    ]} dataKey="value" nameKey="name" outerRadius={80} label />
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </Panel>
      </div>

      <div>
        <Panel title="Email View & AI Reply">
          {activeEmail ? (
            <div>
              <div style={{ marginBottom: 8 }}>
                <div style={{ fontWeight: 600 }}>{activeEmail.subject}</div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>{activeEmail.sender} · {new Date(activeEmail.received_at).toLocaleString()}</div>
              </div>
              <pre style={{ background: '#0f1a33', padding: 12, borderRadius: 12, whiteSpace: 'pre-wrap' }}>{activeEmail.body}</pre>
              <h3>AI Draft</h3>
              <textarea value={reply} onChange={e => setReply(e.target.value)} rows={10} style={{ width: '100%', padding: 12, borderRadius: 12, border: '1px solid #1d2a44', background: '#0f1a33', color: 'white' }} />
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                <button onClick={sendReply} style={btnStyle}>Send Reply</button>
                <button onClick={resolve} style={{ ...btnStyle, background: '#2b3a64' }}>Mark Resolved</button>
              </div>
            </div>
          ) : (
            <div style={{ opacity: 0.7 }}>Select an email on the left to view & reply.</div>
          )}
        </Panel>
      </div>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div style={{ background: '#0c162b', padding: 12, borderRadius: 16, border: '1px solid #172038', marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0 }}>{title}</h2>
      </div>
      <div>{children}</div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div style={{ background: '#0f1a33', padding: 10, borderRadius: 10, border: '1px solid #172038', minWidth: 90, textAlign: 'center' }}>
      <div style={{ fontSize: 12, opacity: 0.7 }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

function Badge({ children, color }) {
  return (
    <span style={{ background: color, color: 'black', fontWeight: 600, padding: '2px 8px', borderRadius: 999, fontSize: 12, marginRight: 6 }}>{children}</span>
  );
}

const btnStyle = { background: '#3b82f6', border: 'none', color: 'white', padding: '10px 14px', borderRadius: 10, cursor: 'pointer', fontWeight: 700 };
