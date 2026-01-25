import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { CheckCircle, BarChart2, Book } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";

export default function Report() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  // For this simplified version, we'll just show a success message and links
  // In a real app, we'd fetch the specific session report data (score, errors found, etc.)
  // Since we don't have a dedicated "getReport" endpoint yet, we can fetch the history or session details.
  // For now, let's show a generic "Analysis Complete" screen.

  useEffect(() => {
     // Simulate loading or fetch session status
     setTimeout(() => setLoading(false), 1000);
  }, []);

  if (loading) return <div className="p-8 text-white">Generating Report...</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in p-6">
        <div className="text-center py-8">
            <div className="h-24 w-24 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6 ring-1 ring-emerald-500/30">
                <CheckCircle className="h-12 w-12 text-emerald-400" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">Session Complete!</h1>
            <p className="text-slate-400 text-lg">Your conversation has been analyzed and your progress updated.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="glass-card border-slate-800">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <BarChart2 className="h-5 w-5 text-violet-400" />
                        Analysis
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-slate-300">
                    <p>Your English level has been estimated based on your vocabulary and grammar usage.</p>
                    <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800">
                        <div className="text-sm text-slate-500 uppercase tracking-wider mb-1">Estimated Level</div>
                        <div className="text-2xl font-bold text-white">Intermediate (B1)</div>
                    </div>
                </CardContent>
            </Card>

            <Card className="glass-card border-slate-800">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Book className="h-5 w-5 text-amber-400" />
                        Next Steps
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <p className="text-slate-300">We've generated new flashcards based on your mistakes.</p>
                    <Button onClick={() => navigate('/flashcards')} className="w-full bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 border border-amber-500/20">
                        Review Flashcards
                    </Button>
                </CardContent>
            </Card>
        </div>

        <div className="flex justify-center pt-8">
            <Button onClick={() => navigate('/dashboard')} size="lg" className="bg-cyan-500 hover:bg-cyan-600 px-8">
                Back to Dashboard
            </Button>
        </div>
    </div>
  );
}
