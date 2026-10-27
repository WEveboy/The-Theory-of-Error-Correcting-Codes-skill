import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

export const name = 'dsh-boolean-vector-research';
export const inject = ['skills'];
const directory = new URL('./skills/boolean-vector-research/', import.meta.url);
const markdown = readFileSync(new URL('SKILL.md', directory), 'utf8');
const boundary = markdown.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/);
if (!boundary) throw new Error('The packaged skill requires YAML frontmatter');
const content = markdown.slice(boundary[0].length);

export function apply(context) {
  return context.skills.register({
    name: 'boolean-vector-research',
    description: '第一版：布尔函数与向量值函数的构造、精确指标、给定等价证书和可复算实验审计。',
    content,
    invocation: { modelInvocable: true, userInvocable: true },
    provider: name,
    source: 'bundled',
    resourceBase: { kind: 'directory', path: fileURLToPath(directory) },
  });
}
