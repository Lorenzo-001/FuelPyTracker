import React from "react"
import { NavLink } from "react-router-dom"
import {
  Gauge,
  Fuel,
  Wrench,
  CalendarClock,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Car,
  ShieldCheck,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { useReminders } from "@/hooks/useReminders"

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
  badgeVariant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning" | "info"
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { data: reminders } = useReminders()
  const overdueCount = reminders?.filter((r) => r.is_overdue).length || 0
  const urgentCount =
    reminders?.filter((r) => r.progress >= 0.7 && !r.is_overdue).length || 0
  const totalAlerts = overdueCount + urgentCount

  const navItems: NavItem[] = React.useMemo(
    () => [
      {
        title: "Dashboard",
        href: "/",
        icon: Gauge,
      },
      {
        title: "Rifornimenti",
        href: "/fuel",
        icon: Fuel,
      },
      {
        title: "Manutenzioni",
        href: "/maintenance",
        icon: Wrench,
      },
      {
        title: "Promemoria",
        href: "/reminders",
        icon: CalendarClock,
        badge: totalAlerts > 0 ? String(totalAlerts) : undefined,
        badgeVariant: overdueCount > 0 ? "destructive" : "warning",
      },
      {
        title: "Report & Export",
        href: "/reports",
        icon: BarChart3,
      },
      {
        title: "Impostazioni",
        href: "/settings",
        icon: Settings,
      },
    ],
    [totalAlerts, overdueCount]
  )

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-border/80 bg-card/60 backdrop-blur-md transition-all duration-300 ease-in-out select-none z-30",
        collapsed ? "w-18" : "w-64"
      )}
    >
      {/* Brand Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border/60">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 text-slate-950 shadow-md shadow-emerald-500/25">
            <Fuel className="h-5 w-5" />
          </div>
          {!collapsed && (
            <div className="flex flex-col truncate">
              <span className="font-bold text-base tracking-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
                FuelPyTracker
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-400/90">
                Versione 2.0
              </span>
            </div>
          )}
        </div>

        {/* Desktop Collapse Toggle */}
        <button
          type="button"
          onClick={onToggle}
          aria-label={collapsed ? "Espandi barra laterale" : "Comprimi barra laterale"}
          className="hidden md:flex h-7 w-7 items-center justify-center rounded-lg border border-border/60 bg-muted/30 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1.5 p-3 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.href}
              to={item.href}
              end={item.href === "/"}
              className={({ isActive }) =>
                cn(
                  "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150 relative",
                  isActive
                    ? "bg-emerald-500/10 text-emerald-400 font-semibold shadow-xs"
                    : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
                  collapsed && "justify-center px-2"
                )
              }
              title={collapsed ? item.title : undefined}
            >
              {({ isActive }) => (
                <>
                  <div className="relative flex items-center justify-center">
                    <Icon
                      className={cn(
                        "h-5 w-5 shrink-0 transition-transform duration-150 group-hover:scale-110",
                        isActive
                          ? "text-emerald-400"
                          : "text-muted-foreground group-hover:text-foreground"
                      )}
                    />
                    {collapsed && item.badge && (
                      <span
                        className={cn(
                          "absolute -top-1 -right-1 h-2 w-2 rounded-full ring-2 ring-background",
                          item.badgeVariant === "destructive" ? "bg-rose-500 animate-pulse" : "bg-amber-400"
                        )}
                      />
                    )}
                  </div>
                  {!collapsed && (
                    <span className="flex-1 truncate">{item.title}</span>
                  )}
                  {!collapsed && item.badge && (
                    <Badge
                      variant={item.badgeVariant || "default"}
                      className="ml-auto px-1.5 py-0 text-[10px] h-5"
                    >
                      {item.badge}
                    </Badge>
                  )}
                  {/* Subtle active indicator bar */}
                  {isActive && (
                    <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-emerald-500" />
                  )}
                </>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Active Vehicle Snippet / Bottom Card */}
      <div className="p-3 border-t border-border/60">
        {collapsed ? (
          <div className="flex justify-center" title="Veicolo attivo: BMW Serie 1 (AB123CD)">
            <div className="h-9 w-9 rounded-lg bg-muted/40 border border-border/60 flex items-center justify-center text-muted-foreground hover:text-foreground">
              <Car className="h-4 w-4" />
            </div>
          </div>
        ) : (
          <div className="rounded-lg border border-border/60 bg-muted/20 p-2.5">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="h-6 w-6 rounded-md bg-emerald-500/15 text-emerald-400 flex items-center justify-center">
                <Car className="h-3.5 w-3.5" />
              </div>
              <div className="flex-1 truncate">
                <div className="text-xs font-semibold text-foreground truncate">
                  BMW Serie 1
                </div>
                <div className="text-[10px] text-muted-foreground">
                  AB 123 CD • Diesel
                </div>
              </div>
              <span title="Veicolo Principale">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
              </span>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}
