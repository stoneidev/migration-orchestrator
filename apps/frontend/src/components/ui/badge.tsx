import * as React from "react"
import { cn } from "@/shared/lib/cn"
const Badge = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & { variant?: string }>(
  ({ className, variant = "default", ...props }, ref) => (
    <div ref={ref} className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors", variant === "destructive" ? "border-transparent bg-red-500 text-white" : variant === "secondary" ? "border-transparent bg-gray-100 text-gray-900" : "border-transparent bg-primary text-primary-foreground", className)} {...props} />
  )
)
Badge.displayName = "Badge"
export { Badge }
