export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'Inter, system-ui, sans-serif', margin: 0, background: '#0b1220', color: 'white' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
          <h1 style={{ fontSize: 28, marginBottom: 8 }}>AI-Powered Communication Assistant</h1>
          <p style={{ opacity: 0.7, marginTop: 0 }}>Support Inbox · Prioritize · Respond</p>
          {children}
        </div>
      </body>
    </html>
  );
}
