import { useEffect, useState } from "react";
import {
  Clock,
  Calendar,
  MessageSquare,
  ChevronRight,
  BookOpen,
  AlertTriangle,
} from "lucide-react";
import { api, type SessionResponse } from "../services/api";
import { useNavigate } from "react-router-dom";
import { cn } from "../lib/utils";

function SkeletonRow() {
  return (
    <div className="glass-card rounded-xl p-6 space-y-3">
      <div className="flex justify-between">
        <div className="space-y-2">
          <div className="skeleton h-5 w-40" />
          <div className="skeleton h-3 w-64" />
        </div>
        <div className="skeleton h-6 w-20 rounded-full" />
      </div>
      <div className="flex gap-6 pt-1">
        <div className="skeleton h-3 w-32" />
        <div className="skeleton h-3 w-20" />
      </div>
    </div>
  );
}

const STATUS_STYLES: Record<string, string> = {
  finished: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  pending_quiz: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  active: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
};

const STATUS_LABELS: Record<string, string> = {
  finished: "Finished",
  pending_quiz: "Awaiting Quiz",
  active: "In Progress",
};

export default function History() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<SessionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getSessionsHistory()
      .then(setSessions)
      .catch(() => setError("Could not load session history."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight gradient-text">Session History</h1>
        <p className="text-slate-400 mt-2">
          {loading ? "Loading sessions..." : `${sessions.length} session${sessions.length !== 1 ? "s" : ""} recorded`}
        </p>
      </div>

      {/* Error state */}
      {error && (
        <div className="glass-card rounded-xl p-8 border-red-500/20 bg-red-950/10 flex items-center gap-4">
          <AlertTriangle className="h-8 w-8 text-red-400 flex-shrink-0" />
          <div>
            <h3 className="text-white font-medium">Failed to load history</h3>
            <p className="text-slate-400 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="space-y-4 stagger">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && sessions.length === 0 && (
        <div className="glass-card rounded-2xl p-16 text-center space-y-6">
          <div className="mx-auto h-20 w-20 bg-slate-800 rounded-full flex items-center justify-center">
            <MessageSquare className="h-10 w-10 text-slate-500" />
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white">No sessions yet</h3>
            <p className="text-slate-500 mt-2">Start a practice conversation to see your history here.</p>
          </div>
          <button
            onClick={() => navigate("/practice")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-xl font-medium transition-colors"
          >
            <MessageSquare className="h-4 w-4" />
            Start Practicing
          </button>
        </div>
      )}

      {/* Sessions list */}
      {!loading && !error && sessions.length > 0 && (
        <div className="space-y-4 stagger">
          {sessions.map((session) => {
            const statusKey = session.status?.toLowerCase() ?? "finished";
            const statusStyle = STATUS_STYLES[statusKey] ?? STATUS_STYLES.finished;
            const statusLabel = STATUS_LABELS[statusKey] ?? "Finished";
            const isFinished = statusKey === "finished";
            const isPendingQuiz = statusKey === "pending_quiz";

            return (
              <div
                key={session.session_id}
                className={cn(
                  "glass-card rounded-xl p-6 transition-all duration-200 group",
                  (isFinished || isPendingQuiz) && "hover:border-cyan-500/30 cursor-pointer hover:bg-slate-800/60"
                )}
                onClick={() => {
                  if (isFinished) navigate(`/report/${session.session_id}`);
                  else if (isPendingQuiz) navigate(`/quiz/${session.session_id}`);
                }}
              >
                <div className="flex justify-between items-start gap-4">
                  <div className="flex items-start gap-4 flex-1 min-w-0">
                    <div className="flex-shrink-0 h-10 w-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center group-hover:border-cyan-500/30 transition-colors">
                      <BookOpen className="h-5 w-5 text-slate-400 group-hover:text-cyan-400 transition-colors" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="text-base font-semibold text-slate-200 group-hover:text-white transition-colors truncate">
                        {session.topic_label || "Unknown Topic"}
                      </h3>
                      {session.topic_description && (
                        <p className="text-slate-500 text-sm line-clamp-1 mt-0.5">{session.topic_description}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <span className={cn("px-3 py-1 rounded-full text-xs font-medium border", statusStyle)}>
                      {statusLabel}
                    </span>
                    {(isFinished || isPendingQuiz) && (
                      <ChevronRight className="h-5 w-5 text-slate-600 group-hover:text-white group-hover:translate-x-1 transition-all" />
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-6 text-sm text-slate-500 mt-4 pl-14">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>
                      {session.started_at
                        ? new Date(session.started_at).toLocaleDateString(undefined, {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })
                        : "Unknown date"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>{session.active_minutes > 0 ? `${Math.round(session.active_minutes)} min` : "< 1 min"}</span>
                  </div>
                  {isFinished && (
                    <span className="text-cyan-400 text-xs font-medium hover:underline">View Report →</span>
                  )}
                  {isPendingQuiz && (
                    <span className="text-amber-400 text-xs font-medium hover:underline">Continue Quiz →</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
