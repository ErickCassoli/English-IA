import { useEffect, useState } from "react";
import { Clock, Calendar } from "lucide-react";
import { api, type SessionResponse } from "../services/api";

export default function History() {
  const [sessions, setSessions] = useState<SessionResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await api.getSessionsHistory();
      setSessions(data);
    } catch (error) {
      console.error("Failed to load history", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-slate-400 p-8">Loading history...</div>;
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <h1 className="text-3xl font-bold text-white tracking-tight text-amber-100 mb-8">Session History</h1>

      {sessions.length === 0 ? (
        <div className="text-slate-500 text-center py-12 bg-slate-900/50 rounded-xl border border-slate-800">
          No past sessions found. Start practicing!
        </div>
      ) : (
        <div className="grid gap-4">
            {sessions.map((session) => (
                <div 
                    key={session.session_id}
                    className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 hover:border-cyan-500/30 transition-colors group"
                >
                    <div className="flex justify-between items-start">
                        <div>
                            <h3 className="text-xl font-semibold text-slate-200 mb-1 group-hover:text-cyan-400 transition-colors">
                                {session.topic_label || "Unknown Topic"}
                            </h3>
                            <p className="text-slate-500 text-sm line-clamp-2 mb-4">
                                {session.topic_description}
                            </p>
                            
                            <div className="flex gap-6 text-sm text-slate-400">
                                <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-slate-500" />
                                    {session.started_at ? new Date(session.started_at).toLocaleString() : "-"}
                                </div>
                                <div className="flex items-center gap-2">
                                    <Clock className="w-4 h-4 text-slate-500" />
                                    {session.active_minutes} min
                                </div>
                            </div>
                        </div>
                        {/* Future: Add 'View Details' button here */}
                    </div>
                </div>
            ))}
        </div>
      )}
    </div>
  );
}
