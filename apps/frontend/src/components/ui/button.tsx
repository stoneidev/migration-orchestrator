import * as React from "react"
import { cn } from "@/shared/lib/cn"

const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: string; size?: string }>(
  ({ className, variant = "default", size = "default", ...props }, ref) => (
    <button ref={ref} className={cn("inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50", variant === "default" ? "bg-primary text-primary-foreground hover:bg-primary/90" : "border border-input bg-background hover:bg-accent", size === "sm" ? "h-9 px-3" : "h-10 px-4 py-2", className)} {...props} />
  )
)
Button.displayName = "Button"

export { Button }
