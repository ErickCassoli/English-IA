import { Outlet } from "react-router-dom";
import { Sidebar } from "../components/Sidebar";

export default function DashboardLayout() {
  return (
    <div className="flex h-screen bg-[#0f172a] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto relative">
        {/* Background glow effects */}
        <div className="absolute top-0 left-0 w-full h-96 bg-cyan-500/5 blur-3xl rounded-full -translate-y-1/2 pointer-events-none" />
        
        <div className="container mx-auto p-8 relative z-10">
            <Outlet />
        </div>
      </main>
    </div>
  );
}
