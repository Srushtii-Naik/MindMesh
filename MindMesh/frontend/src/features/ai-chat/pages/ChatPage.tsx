import { useState } from 'react';
import { motion } from 'framer-motion';
import { ConversationList } from '@/features/ai-chat/components/ConversationList';
import { MessageComposer } from '@/features/ai-chat/components/MessageComposer';
import { MessageList } from '@/features/ai-chat/components/MessageList';
import { SuggestionsPanel } from '@/features/ai-chat/components/SuggestionsPanel';

/**
 * ROADMAP.md Milestone 7 — AI Companion: a conversational interface with
 * persisted history, context-aware replies, and AI-enhanced suggestions,
 * all routed through the AI abstraction layer. Replaces the ComingSoonPage
 * stub that occupied ROUTES.AI_CHAT since Milestone 3.
 */
export function ChatPage() {
  const [activeConversationId, setActiveConversationId] = useState<string | undefined>(undefined);

  const handleSelect = (conversationId: string) => {
    setActiveConversationId(conversationId || undefined);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto flex h-[calc(100vh-4rem)] max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6 lg:px-8"
    >
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-brand-700 dark:text-brand-300">
          AI Companion
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Ask MindMesh anything — it knows what&apos;s on your plate today.
        </p>
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 md:grid-cols-[220px_1fr_260px]">
        <aside className="rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
          <ConversationList activeConversationId={activeConversationId} onSelect={handleSelect} />
        </aside>

        <section className="flex min-h-0 flex-col gap-4 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <div className="flex-1 overflow-y-auto">
            <MessageList conversationId={activeConversationId} />
          </div>
          {activeConversationId && <MessageComposer conversationId={activeConversationId} />}
        </section>

        <aside className="rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
          <h2 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-300">
            Suggestions
          </h2>
          <SuggestionsPanel />
        </aside>
      </div>
    </motion.div>
  );
}
