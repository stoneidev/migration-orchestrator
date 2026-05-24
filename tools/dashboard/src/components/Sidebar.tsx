"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { group: "Workspace", items: [
    { href: "/", label: "Dashboard" },
    { href: "/review", label: "Review Queue", count: "7" },
    { href: "/pages", label: "Pages", count: "707" },
    { href: "/cost", label: "Cost Analysis" },
  ]},
  { group: "Modules", items: [
    { href: "/pages?module=shop_admin", label: "shop_admin", count: "469" },
    { href: "/pages?module=core", label: "core", count: "100" },
    { href: "/pages?module=bbs", label: "bbs", count: "61" },
    { href: "/pages?module=sms_admin", label: "sms_admin", count: "28" },
    { href: "/pages?module=interad", label: "interad", count: "20" },
    { href: "/pages?module=affiliate", label: "affiliate", count: "18" },
  ]},
  { group: "Intelligence", items: [
    { href: "/patterns", label: "Patterns", count: "142" },
  ]},
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>Silicon2 <span>Migration</span></h1>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((group) => (
          <div className="nav-group" key={group.group}>
            <div className="nav-group-label">{group.group}</div>
            {group.items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-link ${pathname === item.href ? "active" : ""}`}
              >
                {item.label}
                {item.count && <span className="count">{item.count}</span>}
              </Link>
            ))}
          </div>
        ))}
      </nav>
      <div style={{ padding: "12px 16px", borderTop: "1px solid var(--border)", fontSize: 11, color: "var(--text3)" }}>
        v0.1.0 · sk-main-php/adm · 1,099 pages
      </div>
    </aside>
  );
}
