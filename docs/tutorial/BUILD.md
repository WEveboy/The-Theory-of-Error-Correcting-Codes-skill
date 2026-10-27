# 教程源与编译

- Codex-First-Edition.tex：独立完整的Codex教程源。
- DeepSeek-First-Edition.tex：独立完整的DeepSeek Harness教程源。
- codex/main.tex、deepseek/main.tex是Codex内置LaTeX编辑器的项目主文件，与对应导出源内容一致。
- 两份PDF各19页，均从安装仓颉cangjie-skill开始；使用XeLaTeX、CTeX及Fandol字体。

在本目录依次执行，每份运行两次以更新目录和链接：

```powershell
xelatex -interaction=nonstopmode -halt-on-error Codex-First-Edition.tex
xelatex -interaction=nonstopmode -halt-on-error Codex-First-Edition.tex
xelatex -interaction=nonstopmode -halt-on-error DeepSeek-First-Edition.tex
xelatex -interaction=nonstopmode -halt-on-error DeepSeek-First-Edition.tex
```

发行时只提交最终TeX与PDF，aux/log/toc/out等中间文件不进入main。修改后重新编译、检查日志并渲染查看，不以“存在PDF文件”代替验证。

本次内置编译检查未及时返回，最终发行物由本机TeX Live 2024的XeLaTeX实际编译；首次补齐amssymb，再修正长链接换行，最终无Undefined control sequence、Missing character或Overfull警告。
