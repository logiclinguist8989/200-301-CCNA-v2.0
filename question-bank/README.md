# CCNA-style question bank

Practice questions written in the formats used by the Cisco CCNA 200-301 exam — multiple choice,
"choose two", drag and drop (order and match), "refer to the exhibit", testlets and CLI questions.
There is one file per chapter (`ch01.md` … `ch28.md`), and each question names the guide section it
comes from.

The [study website](https://logiclinguist8989.github.io/200-301-CCNA-v2.0/) turns these files into
interactive questions in each chapter and in exam mode. You can also read them directly on GitHub —
note that the answers are visible here.

> These questions are original practice material written for this guide. They are not taken from any
> Cisco exam.

## File format

Questions sit under `## Questions`, or under a `## Testlet <letter> · <title>` heading whose text
(scenario and exhibit) is shared by the questions that follow it. Separate questions with `---`.
Every question has a heading, a source line, the question text and an explanation:

````markdown
### Q1 · Multiple choice
<sub>Source: 1B.7</sub>

Refer to the exhibit.

```
SW1# show interfaces status
...
```

Which port has its speed and duplex configured manually?

- [ ] Fa0/1
- [x] Fa0/2

> **Explanation:** Why the answer is right and the others are wrong.
````

| Heading | Answer format |
| --- | --- |
| `### Qn · Multiple choice` | `- [ ]` options with exactly one `- [x]` |
| `### Qn · Multiple choice — choose two` (or `three`) | that many `- [x]` options |
| `### Qn · Drag and drop — order` | a numbered list in the **correct** order (the website shuffles it) |
| `### Qn · Drag and drop — match` | a two-column table of item → target; an optional `**Extra targets:** a · b` line adds distractors; a target may be used more than once |
| `### Qn · CLI` | `**Prompt:** \`SW1(config-if)#\`` and `**Accepted:** \`command\` · \`other form\`` |

**CLI answers** are checked the way IOS reads commands: keywords may be abbreviated (`sw mode tr`),
interface names may be shortened (`g0/1`), and letter case and extra spaces are ignored. Values such
as VLAN numbers and addresses must match exactly. List any genuinely different command that is also
correct as another accepted answer.

Images use paths relative to this folder, for example `![Figure 1.10](../assets/figures/ch01/fig-01-10-lab-topology.svg)`.

## Checking the bank

```bash
python3 tools/question_bank.py          # validates every file and prints a summary
python3 tools/question_bank.py --json   # the parsed bank, as used by the website
```

The checker fails on a missing source line or explanation, a wrong number of correct options, an
order or match question with too few items, and duplicate question numbers.
