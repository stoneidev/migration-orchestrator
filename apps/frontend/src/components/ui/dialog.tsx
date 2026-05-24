import * as React from "react"
import { cn } from "@/shared/lib/cn"
const Dialog = ({ children, open, onOpenChange }: { children: React.ReactNode; open?: boolean; onOpenChange?: (open: boolean) => void }) => open ? <>{children}</> : null
const DialogTrigger = ({ children, asChild, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { asChild?: boolean }) => <button {...props}>{children}</button>
const DialogContent = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => <div className={cn("fixed inset-0 z-50 flex items-center justify-center", className)} {...props}><div className="fixed inset-0 bg-black/50" /><div className="relative bg-background rounded-lg p-6 shadow-lg max-w-lg w-full">{children}</div></div>
const DialogHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => <div className={cn("flex flex-col space-y-1.5 text-center sm:text-left mb-4", className)} {...props} />
const DialogTitle = ({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => <h2 className={cn("text-lg font-semibold leading-none tracking-tight", className)} {...props} />
export { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle }
