import { useEffect, useState } from "react";
import { Clock, Book, MessageCircle, BarChart2, ChevronRight, Sparkles } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { cn } from "../lib/utils";
import { api, type DashboardSummary } from "../services/api";
import { useNavigate } from "react-router-dom";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../components/ui/tooltip";

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    api.getDashboardStats().then(setStats).catch(console.error);
  }, []);

  const data = stats || {
    study_time_hours: 0,
    study_time_total_seconds: 0,
    words_learned: 0,
    conversations: 0,
    fluency_level: 'A1',
    fluency_score: 0,
    is_assessed: false,
    skills: { reading: 0, writing: 0, listening: 0, speaking: 0 },
    due_flashcards: 0,
    current_streak_days: 0
  };

  const hours = Math.floor((data.study_time_total_seconds || 0) / 3600);
  const minutes = Math.floor(((data.study_time_total_seconds || 0) % 3600) / 60);
  const timeString = `${hours}h ${minutes}m`;

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
            <h1 className="text-4xl font-bold text-white tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">Dashboard</h1>
            <p className="text-slate-400 mt-2 text-lg">Track your English learning progress</p>
        </div>
        <div className="hidden md:block">
            <span className="inline-flex items-center px-4 py-2 rounded-full bg-cyan-500/10 text-cyan-400 text-sm font-medium border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.2)]">
                <Sparkles className="w-4 h-4 mr-2" />
                Streak: {data.current_streak_days} Day{data.current_streak_days !== 1 && 's'}
            </span>
        </div>
      </div>

      {/* Stats Grid */}
      {!data.is_assessed ? (
        <div className="col-span-1 md:col-span-2 lg:col-span-4 glass-card p-12 border-amber-500/30 bg-amber-950/20 rounded-3xl text-center space-y-6 relative overflow-hidden">
             
             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-amber-500 to-transparent opacity-50" />
             
             <div className="mx-auto w-20 h-20 bg-amber-500/20 rounded-full flex items-center justify-center mb-6 ring-1 ring-amber-500/50 shadow-[0_0_30px_rgba(245,158,11,0.2)]">
                <BarChart2 className="h-10 w-10 text-amber-500" />
             </div>

             <div className="max-w-xl mx-auto space-y-4">
                 <h2 className="text-3xl font-bold text-white">Placement Test Required</h2>
                 <p className="text-slate-300 text-lg">
                    To personalize your learning path, we need to determine your initial English level (A1-C2). 
                    This will clear any potential previous data to set a clean baseline.
                 </p>
             </div>

             <div className="pt-4">
                <button 
                    onClick={async () => {
                        if(confirm("This will reset all data and start the test. Continue?")) {
                            try {
                                setStats(null); // Show loading
                                await api.resetData();
                                navigate('/placement');
                            } catch (e) {
                                alert("Failed to start placement test");
                                window.location.reload();
                            }
                        }
                    }}
                    className="px-8 py-4 bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl text-white font-bold text-lg shadow-xl hover:scale-105 hover:shadow-2xl transition-all duration-300 ring-2 ring-white/10"
                >
                    Start Placement Test &rarr;
                </button>
             </div>
        </div>
      ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard 
            title="Study Time" 
            value={timeString} 
            icon={Clock} 
            color="text-cyan-400" 
            bg="bg-cyan-500/10"
            border="border-cyan-500/20"
        />
        <StatsCard 
            title="Words Learned" 
            value={data.words_learned.toLocaleString()} 
            icon={Book} 
            color="text-amber-400" 
            bg="bg-amber-500/10"
            border="border-amber-500/20"
        />
        <StatsCard 
            title="Conversations" 
            value={data.conversations.toString()} 
            icon={MessageCircle} 
            color="text-emerald-400" 
            bg="bg-emerald-500/10"
            border="border-emerald-500/20"
        />
        <TooltipProvider delayDuration={0}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div className="cursor-help">
                        <StatsCard 
                            title="English Level" 
                            value={data.fluency_level} 
                            icon={BarChart2} 
                            color="text-violet-400" 
                            bg="bg-violet-500/10"
                            border="border-violet-500/20"
                        />
                    </div>
                </TooltipTrigger>
                <TooltipContent className="p-4 bg-slate-900/95 border-slate-700 backdrop-blur-xl w-64">
                    <div className="space-y-3">
                        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                             <span className="font-semibold text-white">Skill Breakdown</span>
                             <span className="text-xs text-slate-400">Score / 100</span>
                        </div>
                        {Object.entries(data.skills || {}).map(([skill, score]) => (
                            <div key={skill} className="space-y-1">
                                <div className="flex justify-between text-xs">
                                    <span className="capitalize text-slate-300">{skill}</span>
                                    <span className="text-cyan-400 font-medium">{Math.round(score)}</span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500" 
                                        style={{ width: `${score}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
      </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Quick Actions */}
        <div className="glass-card rounded-2xl p-6 hover:border-slate-600/50 transition-colors group">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-white">Quick Actions</h3>
            <p className="text-slate-400 text-sm mt-1">Start learning right away</p>
          </div>
          <div className="space-y-4">
            <div className={cn("space-y-4", !data.is_assessed && "opacity-50 pointer-events-none grayscale")}>
                <ActionButton 
                    title="Practice Conversation" 
                    desc="Chat with AI in English" 
                    icon={MessageCircle}
                    color="from-cyan-500 to-blue-600"
                    iconColor="text-white"
                    onClick={() => navigate('/practice')}
                />
                <ActionButton 
                    title={`Review Flashcards ${data.due_flashcards > 0 ? `(${data.due_flashcards})` : ''}`} 
                    desc="Memorize new vocabulary" 
                    icon={Book}
                    color="from-amber-500 to-orange-600"
                    iconColor="text-white"
                    onClick={() => navigate('/flashcards')}
                />
            </div>
          </div>
        </div>

        {/* Learning Tips */}
        <div className="glass-card rounded-2xl p-6 hover:border-slate-600/50 transition-colors">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-white">Learning Tips</h3>
            <p className="text-slate-400 text-sm mt-1">Make the most of your practice</p>
          </div>
          <ul className="space-y-4">
                {[
                    'Practice daily for at least 15 minutes', 
                    'Use new words in conversations', 
                    'Review flashcards regularly', 
                    'Don\'t be afraid to make mistakes'
                ].map((tip, i) => (
                    <li key={i} className="flex items-start space-x-3 text-slate-300 group">
                        <div className="h-2 w-2 rounded-full bg-cyan-500 mt-2 group-hover:scale-125 transition-transform shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
                        <span className="group-hover:text-white transition-colors">{tip}</span>
                    </li>
                ))}
            </ul>
        </div>
      </div>
    </div>
  );
}

function StatsCard({ title, value, icon: Icon, color, bg, border }: any) {
    return (
        <Card className={cn("glass-card border-slate-800 transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl hover:bg-slate-800/60", border)}>
            <CardContent className="p-6 flex items-center justify-between relative overflow-hidden">
                <div className="relative z-10">
                    <p className="text-sm font-medium text-slate-400">{title}</p>
                    <h3 className="text-3xl font-bold text-white mt-1 tracking-tight">{value}</h3>
                </div>
                <div className={cn("p-3 rounded-xl backdrop-blur-md", bg)}>
                    <Icon className={cn("h-6 w-6", color)} />
                </div>
                {/* Glow effect */}
                <div className={cn("absolute -bottom-6 -right-6 w-24 h-24 rounded-full blur-3xl opacity-20", bg.replace('/10', ''))} />
            </CardContent>
        </Card>
    )
}

function ActionButton({ title, desc, icon: Icon, color, iconColor, onClick }: any) {
    return (
        <button 
            onClick={onClick}
            className="w-full flex items-center p-4 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/10 transition-all group text-left relative overflow-hidden"
        >
            <div className={cn("p-3 rounded-lg bg-gradient-to-br shadow-lg group-hover:scale-110 transition-transform duration-300", color)}>
                <Icon className={cn("h-6 w-6", iconColor)} />
            </div>
            <div className="ml-4 flex-1 relative z-10">
                <h4 className="text-white font-medium group-hover:text-cyan-400 transition-colors text-lg">{title}</h4>
                <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">{desc}</p>
            </div>
            <ChevronRight className="h-5 w-5 text-slate-600 group-hover:text-white group-hover:translate-x-1 transition-all" />
        </button>
    )
}
