import * as React from "react"
import { cn } from "@/shared/lib/cn"
const Tabs = ({ className, children, defaultValue, ...props }: React.HTMLAttributes<HTMLDivElement> & { defaultValue?: string }) => <div className={cn("", className)} {...props}>{children}</div>
const TabsList = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => <div className={cn("inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground", className)} {...props}>{children}</div>
const TabsTrigger = ({ className, children, value, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { value?: string }) => <button className={cn("inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm", className)} {...props}>{children}</button>
const TabsContent = ({ className, children, value, ...props }: React.HTMLAttributes<HTMLDivElement> & { value?: string }) => <div className={cn("mt-2 ring-offset-background focus-visible:outline-none", className)} {...props}>{children}</div>
export { Tabs, TabsList, TabsTrigger, TabsContent }
