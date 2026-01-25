import { Info } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";

export interface DetectedError {
  start: number;
  end: number;
  category: string;
  user_text: string;
  corrected_text: string;
  note: string;
}

interface CorrectionPopoverProps {
  errors: DetectedError[];
}

export function CorrectionPopover({ errors }: CorrectionPopoverProps) {
  if (!errors || errors.length === 0) return null;

  return (
    <TooltipProvider>
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>
          <button 
            className="ml-2 inline-flex items-center justify-center p-0.5 rounded-full hover:bg-cyan-500/20 transition-colors cursor-help group"
            aria-label="View corrections"
          >
            <Info className="h-4 w-4 text-cyan-400/70 group-hover:text-cyan-400" />
          </button>
        </TooltipTrigger>
        <TooltipContent className="w-80 p-0 bg-slate-900 border-slate-700 shadow-xl z-50">
          <div className="p-4 border-b border-slate-700 bg-slate-900/50">
            <h4 className="font-semibold text-white flex items-center text-sm">
              <Info className="h-4 w-4 mr-2 text-cyan-400" />
              Suggested Corrections
            </h4>
          </div>
          <div className="p-4 space-y-3 max-h-80 overflow-y-auto">
            {errors.map((error, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex items-start gap-2">
                  <span className="text-[10px] font-bold tracking-wider text-slate-500 uppercase bg-slate-800 px-1.5 py-0.5 rounded">{error.category}</span>
                </div>
                <div className="grid gap-1">
                  <div className="text-sm">
                    <span className="text-red-400 line-through opacity-80 decoration-red-500/50">{error.user_text}</span>
                    <span className="mx-2 text-slate-500">→</span>
                    <span className="text-green-400 font-medium">{error.corrected_text}</span>
                  </div>
                  <p className="text-xs text-slate-400 italic">{error.note}</p>
                </div>
                {idx < errors.length - 1 && (
                  <div className="border-t border-slate-800 pt-2 mt-2" />
                )}
              </div>
            ))}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
