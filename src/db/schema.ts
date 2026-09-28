import { pgTable, serial, varchar, text, timestamp, integer } from "drizzle-orm/pg-core";

export const findings = pgTable("findings", {
  id: serial("id").primaryKey(),
  severity: varchar("severity", { length: 20 }).notNull(),
  scanner: varchar("scanner", { length: 50 }).notNull(),
  ruleId: varchar("rule_id", { length: 255 }).notNull(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  category: varchar("category", { length: 100 }),
  filePath: text("file_path").notNull(),
  startLine: integer("start_line"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});
