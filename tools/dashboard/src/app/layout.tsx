export const metadata = { title: "Silicon2 Migration Orchestrator" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
        />
      </head>
      <body style={{ margin: 0, background: "#09090b", color: "#fafafa", fontFamily: "'Pretendard Variable', sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
