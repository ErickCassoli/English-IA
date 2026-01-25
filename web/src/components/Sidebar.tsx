import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { LayoutDashboard, MessageSquare, CreditCard, LifeBuoy, BookOpen, Settings } from "lucide-react";
import { cn } from "../lib/utils";
import { api } from "../services/api";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Flashcards", href: "/flashcards", icon: CreditCard },
  { name: "Practice", href: "/practice", icon: LifeBuoy },
];

export function Sidebar() {
  const [isAssessed, setIsAssessed] = useState(true);

  useEffect(() => {
      api.getDashboardStats().then(s => setIsAssessed(s.is_assessed)).catch(console.error);
  }, []);

  return (
    <div className="flex flex-col h-screen w-72 bg-[#0B1120] border-r border-slate-800/80 text-slate-100 relative overflow-hidden">
        {/* Decorative glow */}
        <div className="absolute top-0 left-0 w-full h-40 bg-cyan-500/10 blur-3xl pointer-events-none" />

      <div className="p-8 flex items-center space-x-3 relative z-10">
        <div className="h-10 w-10 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.3)]">
            <BookOpen className="text-white h-6 w-6" />
        </div>
        <div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 block tracking-tight">
            EnglishAI
            </span>
            <span className="text-[10px] uppercase tracking-wider text-cyan-400 font-semibold">Offline Mode</span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2 relative z-10">
        <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Menu</p>
        
        {navigation.filter(item => {
            if (!isAssessed && (item.name === 'Chat' || item.name === 'Practice' || item.name === 'Flashcards')) return false;
            return true;
        }).map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                "flex items-center justify-between px-4 py-3.5 rounded-xl transition-all duration-300 group",
                isActive
                  ? "bg-gradient-to-r from-cyan-500/10 to-transparent text-white font-medium border-l-2 border-cyan-500"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              )
            }
          >
           {({ isActive }) => (
            <>
                <div className="flex items-center space-x-3">
                    <item.icon className={cn("h-5 w-5 transition-colors", isActive ? "text-cyan-400" : "text-slate-500 group-hover:text-slate-300")} />
                    <span>{item.name}</span>
                </div>
                {isActive && <div className="h-1.5 w-1.5 rounded-full bg-cyan-400 shadow-[0_0_5px_rgba(6,182,212,0.8)]" />}
            </>
           )}
          </NavLink>
        ))}
        

      </nav>

      <div className="p-4 border-t border-slate-800/80 bg-slate-900/30">
        <NavLink 
            to="/settings"
            className={({ isActive }) => cn(
                "flex items-center space-x-3 px-4 py-3 w-full rounded-xl transition-colors",
                isActive ? "text-cyan-400 bg-slate-800/50" : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
            )}
        >
            <Settings className="h-5 w-5" />
            <span>Settings</span>
        </NavLink>
      </div>
    </div>
  );
}
