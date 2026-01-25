import { useEffect, useState } from "react";
import { MessageSquare, Plus, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { Button } from "./ui/button";
import { Card } from "./ui/card";

interface TopicSelectorProps {
    onSelect: (topicCode: string | null, customTopic?: string) => void;
}

export function TopicSelector({ onSelect }: TopicSelectorProps) {
    const [recent, setRecent] = useState<{code: string, label: string, description: string}[]>([]);
    const [custom, setCustom] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getRecentTopics().then(setRecent).finally(() => setLoading(false));
    }, []);

    const handleCustom = () => {
        if (!custom.trim()) return;
        onSelect(null, custom);
    };

    return (
        <div className="absolute inset-0 z-20 flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-sm animate-in fade-in">
            <Card className="w-full max-w-lg bg-[#0B1120] border-slate-700 shadow-2xl p-6 space-y-6">
                <div className="text-center space-y-2">
                    <div className="mx-auto w-12 h-12 bg-cyan-500/10 rounded-full flex items-center justify-center mb-2 ring-1 ring-cyan-500/30">
                        <MessageSquare className="w-6 h-6 text-cyan-400" />
                    </div>
                    <h2 className="text-2xl font-bold text-white">Choose a Topic</h2>
                    <p className="text-slate-400 text-sm">Select a recent topic or start something new to begin chatting.</p>
                </div>

                {/* Recent / Suggested */}
                <div className="space-y-3">
                    <h3 className="text-xs uppercase tracking-wider text-slate-500 font-semibold flex items-center">
                        <RefreshCw className="w-3 h-3 mr-1" /> Recent & Suggested
                    </h3>
                    <div className="grid grid-cols-1 gap-2">
                        {loading && <div className="text-slate-500 text-sm italic">Loading topics...</div>}
                        {recent.map((t, i) => (
                            <button
                                key={i}
                                onClick={() => onSelect(t.code)}
                                className="flex items-center p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-700 hover:border-cyan-500/50 transition-all text-left group"
                            >
                                <div className="ml-2">
                                    <span className="block text-slate-200 font-medium group-hover:text-cyan-400 transition-colors">{t.label}</span>
                                    <span className="block text-xs text-slate-500">{t.description}</span>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t border-slate-800" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-[#0B1120] px-2 text-slate-500">Or Custom Topic</span>
                    </div>
                </div>

                {/* Custom Input */}
                <div className="flex gap-2">
                    <input
                        className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder:text-slate-500 focus:ring-1 focus:ring-cyan-500 outline-none"
                        placeholder="e.g. Space Travel, Cooking..."
                        value={custom}
                        onChange={(e) => setCustom(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleCustom()}
                    />
                    <Button onClick={handleCustom} disabled={!custom.trim()} className="bg-cyan-600 hover:bg-cyan-500">
                        <Plus className="w-4 h-4" />
                    </Button>
                </div>
            </Card>
        </div>
    );
}
