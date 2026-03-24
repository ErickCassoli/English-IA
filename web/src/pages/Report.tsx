import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  CheckCircle,
  BarChart2,
  Book,
  AlertTriangle,
  Star,
  TrendingUp,
  MessageCircle,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { api, type ReportResponse } from "../services/api";
import { cn } from "../lib/utils";

export default function Report() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    api
      .getReport(sessionId)
      .then(setReport)
      .catch((err) => {
        console.error(err);
        setError("Could not load report. The session might still be processing.");
      })
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-10 w-10 text-cyan-400 animate-spin" />
        <p className="text-slate-400 text-lg">Generating your session report...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-lg mx-auto text-center py-20 space-y-6">
        <div className="h-20 w-20 bg-amber-500/10 rounded-full flex items-center justify-center mx-auto ring-1 ring-amber-500/20">
          <AlertTriangle className="h-10 w-10 text-amber-400" />
        </div>
        <h2 className="text-2xl font-bold text-white">Report Unavailable</h2>
        <p className="text-slate-400">{error ?? "No report data found for this session."}</p>
        <div className="flex justify-center gap-4">
          <Button onClick={() => navigate("/dashboard")} className="bg-cyan-500 hover:bg-cyan-600">
            Back to Dashboard
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate("/flashcards")}
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
          >
            View Flashcards
          </Button>
        </div>
      </div>
    );
  }

  const cefrColors: Record<string, string> = {
    A1: "text-slate-300",
    A2: "text-blue-400",
    B1: "text-cyan-400",
    B2: "text-emerald-400",
    C1: "text-violet-400",
    C2: "text-amber-400",
  };

  const cefrColor = cefrColors[report.kpis.cefr_estimate] ?? "text-cyan-400";

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500 pb-10">
      {/* Hero */}
      <div className="text-center py-8">
        <div className="h-24 w-24 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6 ring-1 ring-emerald-500/30 shadow-[0_0_40px_rgba(16,185,129,0.15)]">
          <CheckCircle className="h-12 w-12 text-emerald-400" />
        </div>
        <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">Session Complete!</h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto">{report.summary}</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          label="Words Produced"
          value={String(report.kpis.words)}
          icon={MessageCircle}
          color="text-cyan-400"
          bg="bg-cyan-500/10"
        />
        <KPICard
          label="Errors Detected"
          value={String(report.kpis.errors)}
          icon={AlertTriangle}
          color="text-amber-400"
          bg="bg-amber-500/10"
        />
        <KPICard
          label="Accuracy"
          value={`${report.kpis.accuracy_pct.toFixed(1)}%`}
          icon={TrendingUp}
          color="text-emerald-400"
          bg="bg-emerald-500/10"
        />
        <KPICard
          label="CEFR Estimate"
          value={report.kpis.cefr_estimate}
          icon={BarChart2}
          color={cefrColor}
          bg="bg-violet-500/10"
        />
      </div>

      {/* Quiz Summary */}
      {report.quiz_summary.total > 0 && (
        <Card className="glass-card border-slate-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Star className="h-5 w-5 text-amber-400" />
              Knowledge Check Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-white">
                  {report.quiz_summary.correct}/{report.quiz_summary.total}
                </p>
                <p className="text-slate-400 text-sm mt-1">Questions Correct</p>
              </div>
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-400">Quiz Accuracy</span>
                  <span className="text-white font-semibold">{report.quiz_summary.accuracy_pct.toFixed(0)}%</span>
                </div>
                <div className="h-2.5 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full transition-all duration-700"
                    style={{ width: `${report.quiz_summary.accuracy_pct}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths */}
        {report.strengths.length > 0 && (
          <Card className="glass-card border-slate-800 border-emerald-500/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-emerald-400" />
                Strengths
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {report.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-3 text-slate-300">
                    <div className="h-2 w-2 rounded-full bg-emerald-500 mt-2 flex-shrink-0 shadow-[0_0_6px_rgba(16,185,129,0.6)]" />
                    <span className="text-sm">{s}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Areas for Improvement */}
        {report.improvements.length > 0 && (
          <Card className="glass-card border-slate-800 border-amber-500/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-amber-400" />
                Areas to Improve
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {report.improvements.map((imp, i) => (
                  <li key={i} className="flex items-start gap-3 text-slate-300">
                    <div className="h-2 w-2 rounded-full bg-amber-500 mt-2 flex-shrink-0 shadow-[0_0_6px_rgba(245,158,11,0.6)]" />
                    <span className="text-sm">{imp}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Error Examples */}
      {report.examples.length > 0 && (
        <Card className="glass-card border-slate-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Book className="h-5 w-5 text-cyan-400" />
              Key Corrections to Remember
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {report.examples.map((ex, i) => (
              <div
                key={i}
                className="p-4 bg-slate-900/50 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-sm text-red-400 line-through opacity-80 decoration-red-500/50">
                    {ex.source}
                  </span>
                  <ArrowRight className="h-4 w-4 text-slate-500 flex-shrink-0" />
                  <span className="text-sm text-emerald-400 font-medium">{ex.target}</span>
                </div>
                {ex.note && <p className="text-xs text-slate-500 italic">{ex.note}</p>}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Next Steps */}
      <Card className="glass-card border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <ArrowRight className="h-5 w-5 text-violet-400" />
            Next Steps
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={() => navigate("/flashcards")}
            className="flex-1 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 border border-amber-500/20"
          >
            <Book className="mr-2 h-4 w-4" />
            Review Flashcards
          </Button>
          <Button
            onClick={() => navigate("/practice")}
            className="flex-1 bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/20"
          >
            <MessageCircle className="mr-2 h-4 w-4" />
            Practice Again
          </Button>
          <Button
            onClick={() => navigate("/dashboard")}
            className="flex-1 bg-violet-500/10 text-violet-400 hover:bg-violet-500/20 border border-violet-500/20"
          >
            <BarChart2 className="mr-2 h-4 w-4" />
            Dashboard
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

function KPICard({
  label,
  value,
  icon: Icon,
  color,
  bg,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  color: string;
  bg: string;
}) {
  return (
    <div className={cn("glass-card rounded-2xl p-5 flex flex-col items-center text-center gap-3 hover:scale-[1.02] transition-transform")}>
      <div className={cn("p-3 rounded-xl", bg)}>
        <Icon className={cn("h-6 w-6", color)} />
      </div>
      <p className={cn("text-2xl font-bold tracking-tight", color)}>{value}</p>
      <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">{label}</p>
    </div>
  );
}
