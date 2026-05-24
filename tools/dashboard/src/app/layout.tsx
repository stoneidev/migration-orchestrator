import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

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
      <body>
        <div className="app-layout">
          <Sidebar />
          <main className="main">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
