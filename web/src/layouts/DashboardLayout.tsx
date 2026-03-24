import { Outlet } from "react-router-dom";
import { Sidebar } from "../components/Sidebar";

export default function DashboardLayout() {
  return (
    <div className="flex h-screen bg-[#0B1120] overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto relative">
        {/* Ambient background glow */}
        <div className="absolute top-0 left-1/4 w-[600px] h-96 bg-cyan-500/5 blur-[100px] rounded-full pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-64 bg-violet-500/5 blur-[80px] rounded-full pointer-events-none" />

        <div className="container mx-auto p-8 relative z-10 max-w-7xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
