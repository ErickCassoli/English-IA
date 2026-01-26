import { useEffect, useState } from "react";
import { Plus, Trash2, RotateCcw } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../components/ui/button";
import { cn } from "../lib/utils";
import { AddCardModal } from "../components/AddCardModal";

interface Flashcard {
  id: string;
  front: string;
  back: string;
  reps: number;
}

export default function Flashcards() {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [flippedCards, setFlippedCards] = useState<Record<string, boolean>>({});
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  useEffect(() => {
    loadCards();
  }, []);

  const loadCards = async () => {
    try {
      setLoading(true);
      // Fetch ALL cards, not just due ones
      const data = await api.getAllFlashcards();
      setCards(data);
    } catch (error) {
      console.error("Failed to load cards:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleFlip = (id: string) => {
    setFlippedCards(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // Prevent flipping when clicking delete
    if (!confirm("Are you sure you want to delete this card?")) return;

    try {
        await api.deleteFlashcard(id);
        setCards(prev => prev.filter(c => c.id !== id));
    } catch (error) {
        console.error("Failed to delete card:", error);
    }
  };

  if (loading) {
     return <div className="text-slate-400 text-center p-12">Loading collection...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
         <div>
            <h1 className="text-3xl font-bold text-white tracking-tight text-amber-100">My Collection</h1>
            <p className="text-slate-400 mt-2">{cards.length} cards in your library</p>
         </div>
         <Button className="bg-cyan-500 hover:bg-cyan-600" onClick={() => setIsAddModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" /> Add Card
         </Button>
      </div>

      {cards.length === 0 ? (
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center max-w-md w-full mx-auto">
              <RotateCcw className="h-16 w-16 text-slate-600 mx-auto mb-6" />
              <h3 className="text-xl font-semibold text-slate-200">Empty Library</h3>
              <p className="text-slate-500 mt-2 mb-8">Start adding cards to build your knowledge base.</p>
              <Button className="bg-cyan-500 hover:bg-cyan-600" onClick={() => setIsAddModalOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" /> Add Card
              </Button>
          </div>
      ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-12">
            {cards.map(card => {
                const isFlipped = flippedCards[card.id] || false;
                
                return (
                    <div 
                        key={card.id}
                        className="relative h-64 w-full cursor-pointer group perspective-1000"
                        onClick={() => toggleFlip(card.id)}
                    >
                        <div className={cn(
                            "w-full h-full transition-all duration-500 preserve-3d relative",
                            isFlipped ? "rotate-y-180" : ""
                        )}>
                            {/* Front */}
                            <div className="absolute inset-0 backface-hidden bg-slate-800 border-2 border-slate-700 rounded-2xl flex flex-col items-center justify-center p-6 shadow-xl hover:border-cyan-500/30 transition-colors">
                                <span className="text-xs font-bold text-cyan-500/80 mb-2 uppercase tracking-widest absolute top-4">Front</span>
                                <h3 className="text-xl font-semibold text-white text-center line-clamp-4">
                                    {card.front}
                                </h3>
                                <p className="text-slate-500 text-xs absolute bottom-4">Click to flip</p>
                            </div>

                            {/* Back */}
                            <div className="absolute inset-0 backface-hidden rotate-y-180 bg-slate-900 border-2 border-emerald-500/30 rounded-2xl flex flex-col items-center justify-center p-6 shadow-xl">
                                <span className="text-xs font-bold text-emerald-500/80 mb-2 uppercase tracking-widest absolute top-4">Back</span>
                                <h3 className="text-lg font-medium text-slate-200 text-center line-clamp-4">
                                    {card.back}
                                </h3>
                                
                                {/* Actions only visible on Back */}
                                <div className="absolute bottom-4 flex gap-3">
                                    <Button 
                                        variant="destructive" 
                                        size="sm"
                                        className="h-8 px-3 text-xs bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20"
                                        onClick={(e) => handleDelete(e, card.id)}
                                    >
                                        <Trash2 className="h-3 w-3 mr-1" /> Delete
                                    </Button>
                                    <Button 
                                        variant="ghost" 
                                        size="sm"
                                        className="h-8 px-3 text-xs text-slate-400 hover:text-white"
                                        onClick={(e) => { e.stopPropagation(); toggleFlip(card.id); }}
                                    >
                                        Keep
                                    </Button>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            })}
          </div>
      )}
      
      <AddCardModal 
        isOpen={isAddModalOpen} 
        onClose={() => setIsAddModalOpen(false)} 
        onAdded={loadCards} 
      />
    </div>
  );
}
