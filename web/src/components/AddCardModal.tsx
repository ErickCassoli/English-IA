import { useState } from "react";
import { X, Plus, Loader2 } from "lucide-react";
import { api } from "../services/api";
import { Button } from "./ui/button";
import { Card } from "./ui/card";

interface AddCardModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAdded: () => void;
}

export function AddCardModal({ isOpen, onClose, onAdded }: AddCardModalProps) {
    const [front, setFront] = useState("");
    const [back, setBack] = useState("");
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!front.trim() || !back.trim()) return;

        setLoading(true);
        try {
            await api.createFlashcard(front, back);
            setFront("");
            setBack("");
            onAdded();
            onClose();
        } catch (error) {
            console.error(error);
            alert("Failed to add card");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
            <Card className="w-full max-w-md bg-[#0B1120] border-slate-700 shadow-2xl relative overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-slate-800 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-white flex items-center">
                        <Plus className="w-5 h-5 mr-2 text-cyan-400" />
                        Add New Card
                    </h2>
                    <button 
                        onClick={onClose}
                        className="text-slate-400 hover:text-white transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Form */}
                <div className="p-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Front (Question/Word)</label>
                            <textarea
                                className="w-full h-24 bg-slate-900 border border-slate-700 rounded-lg p-3 text-white placeholder:text-slate-500 focus:ring-1 focus:ring-cyan-500 outline-none resize-none"
                                placeholder="e.g. What implies 'Serendipity'?"
                                value={front}
                                onChange={e => setFront(e.target.value)}
                                autoFocus
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-300">Back (Answer/Definition)</label>
                            <textarea
                                className="w-full h-24 bg-slate-900 border border-slate-700 rounded-lg p-3 text-white placeholder:text-slate-500 focus:ring-1 focus:ring-emerald-500 outline-none resize-none"
                                placeholder="e.g. Finding something good without looking for it."
                                value={back}
                                onChange={e => setBack(e.target.value)}
                            />
                        </div>

                        <div className="pt-2 flex justify-end gap-3">
                            <Button 
                                type="button" 
                                variant="ghost" 
                                onClick={onClose}
                                className="text-slate-400 hover:text-white hover:bg-slate-800"
                            >
                                Cancel
                            </Button>
                            <Button 
                                type="submit" 
                                disabled={loading || !front.trim() || !back.trim()}
                                className="bg-cyan-500 hover:bg-cyan-600 text-white min-w-[100px]"
                            >
                                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Add Card"}
                            </Button>
                        </div>
                    </form>
                </div>
            </Card>
        </div>
    );
}
