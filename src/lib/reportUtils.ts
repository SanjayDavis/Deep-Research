/** Strip YAML frontmatter from markdown report content. */
export function stripFrontmatter(content: string): string {
  if (!content.startsWith("---")) return content;
  const parts = content.split("---", 3);
  if (parts.length >= 3) return parts[2].replace(/^\n+/, "");
  return content;
}

/** Remove LLM intent tags like [ANALYZE], [SUPPORTS] from display markdown. */
export function stripIntentTags(content: string): string {
  return content.replace(/\[(SUMMARIZE|ANALYZE|EVIDENCE|CONTEXT|IMPLICATION|CRITIQUE|SUPPORTS|CONTRADICTS|BACKGROUND)\]\s*/g, "");
}

/** Prepare report content for rendered preview. */
export function prepareReportForPreview(content: string): string {
  return stripIntentTags(stripFrontmatter(content));
}

/** Extract title from frontmatter or first heading. */
export function extractReportTitle(content: string): string {
  const fm = content.match(/^---[\s\S]*?title:\s*"([^"]+)"/);
  if (fm) return fm[1];
  const heading = content.match(/^#\s+(.+)$/m);
  if (heading) return heading[1];
  return "Research Report";
}
