import { motion } from 'framer-motion';
import type { Message } from '@/features/ai-chat/types';

interface MessageBubbleProps {
  message: Message;
}

/** A single chat turn, styled by role. Animation kept subtle per
 * PROJECT_RULES.md Section 5 ("used to orient and reassure, never to
 * impress or distract"). */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <motion.li
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
          isUser
            ? 'bg-brand-600 text-white'
            : 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-100'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </motion.li>
  );
}
