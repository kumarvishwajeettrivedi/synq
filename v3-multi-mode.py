import model_interface as models
import os
import json
import re
import subprocess


def strip_markdown(text):
    """Remove markdown formatting for clean terminal output"""
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    
    # Remove italic (*text* or _text_)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Remove code blocks (```code```)
    text = re.sub(r'```[\w]*\n', '', text)
    text = re.sub(r'```', '', text)
    
    # Remove inline code (`code`)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove headers (# Header)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove links [text](url) -> text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    return text

# ==========================================
# MODE 1: CONSENSUS BUILDER (Mentor-Level Judge + Scoring + Feedback)
# ==========================================
def mode_consensus(prompt):
    print("\n Fetching responses from models...\n")

    try:
        gemini_resp = models.query_gemini(prompt) or "No response"
    except Exception as e:
        gemini_resp = f"Error: {e}"

    try:
        groq_resp = models.query_groq(prompt) or "No response"
    except Exception as e:
        groq_resp = f"Error: {e}"

    try:
        openrouter_resp = models.query_openrouter(prompt) or "No response"
    except Exception as e:
        openrouter_resp = f"Error: {e}"

    print(" Responses received. Synthesizing...\n")

    consensus_prompt = f"""
You are a highly experienced mentor and evaluator.
Your tone is strict, clear, confident, and encouraging.
You are not harsh or rude. You maintain high standards and push for excellence.

You MUST perform 3 tasks:

==========================================
TASK 1 — MENTOR SCORING (0–10)
==========================================
Score each model's response on:
- Accuracy
- Depth
- Clarity
- Usefulness
- Completeness
- Reasoning quality

Give a short justification for each score.

==========================================
TASK 2 — MENTOR FEEDBACK
==========================================
Provide constructive, improvement-focused feedback for each model.
Be firm but supportive. Give actionable suggestions.
Avoid insults or rudeness.

==========================================
TASK 3 — FINAL CONSENSUS ANSWER
==========================================
Combine ONLY the strongest parts of the three responses.
Remove:
- Repetition
- Incorrect claims
- Weak reasoning
- Unnecessary fluff

Create a final answer that is:
- Clear
- Correct
- Highly structured
- Deeper than any individual model's output
- Mentor-level quality

==========================================

User Prompt:
\"\"\"{prompt}\"\"\"

Gemini Response:
\"\"\"{gemini_resp}\"\"\"

Groq Response:
\"\"\"{groq_resp}\"\"\"

OpenRouter Response:
\"\"\"{openrouter_resp}\"\"\"

Now produce:

1. Mentor Scoring Table  
2. Mentor Feedback for each model  
3. Final Consensus Answer
"""

    try:
        final = models.query_gemini(consensus_prompt)
        final = strip_markdown(final)  # Remove markdown formatting
    except Exception as e:
        final = f"Consensus generation failed: {e}"

    print("\n FINAL CONSENSUS (MENTOR JUDGE + SCORING + FEEDBACK):\n")
    print(final)



# ==========================================
# MODE 2: DEBATE MODE
# ==========================================
def mode_debate(prompt):
    print("\n REALISTIC COMPETITIVE DEBATE MODE\n")

    # -----------------------------
    # ROUND 1 — Opening Statements
    # -----------------------------
    print("\n ROUND 1: Opening Arguments\n")

    pro_prompt = f"""
You are the PRO side in a competitive academic debate.
Your job:
- Provide a clear, structured opening statement (max 6 sentences)
- Present 2–3 strong, evidence-based points
- No personal attacks, no fluff
- Use logical reasoning and real-world examples

Debate Topic:
{prompt}
"""

    con_prompt = f"""
You are the CON side in a competitive academic debate.
Your job:
- Provide a clear, structured opening statement (max 6 sentences)
- Present 2–3 strong, evidence-based points
- Directly counter the *assumptions* of the PRO side pre-emptively
- Use logical reasoning and real-world examples

Debate Topic:
{prompt}
"""

    pro_arg = models.query_gemini(pro_prompt)
    con_arg = models.query_groq(con_prompt)

    print(f"🔵 PRO (Opening Statement):\n{strip_markdown(pro_arg)}\n")
    print(f"🔴 CON (Opening Statement):\n{strip_markdown(con_arg)}\n")

    # -----------------------------
    # ROUND 2 — Cross-Examination
    # -----------------------------
    print("\n ROUND 2: Cross-Examination\n")

    cross_pro_prompt = f"""
You are the PRO debater.
Cross-examine the CON's opening argument.
Ask 3 sharp, focused questions targeting weaknesses, contradictions, or missing evidence.

CON said:
\"\"\"{con_arg}\"\"\"
"""

    cross_con_prompt = f"""
You are the CON debater.
Cross-examine the PRO's opening argument.
Ask 3 sharp, focused questions targeting assumptions, logic gaps, or unsupported claims.

PRO said:
\"\"\"{pro_arg}\"\"\"
"""

    pro_cross = models.query_gemini(cross_pro_prompt)
    con_cross = models.query_groq(cross_con_prompt)

    print(f"🔵 PRO Questions:\n{strip_markdown(pro_cross)}\n")
    print(f"🔴 CON Questions:\n{strip_markdown(con_cross)}\n")

    # -----------------------------
    # ROUND 3 — Rebuttals
    # -----------------------------
    print("\n ROUND 3: Rebuttals\n")

    rebuttal_pro_prompt = f"""
You are the PRO debater.
Provide a rebuttal to the CON’s argument.
Requirements:
- Address their main points directly
- Expose logical fallacies if any
- Provide better evidence than they used
- Stay concise (max 6 sentences)

CON argument:
\"\"\"{con_arg}\"\"\"
"""

    rebuttal_con_prompt = f"""
You are the CON debater.
Provide a rebuttal to the PRO’s argument.
Requirements:
- Address their main points directly
- Highlight weaknesses and counter-evidence
- Identify fallacies or flawed assumptions
- Stay concise (max 6 sentences)

PRO argument:
\"\"\"{pro_arg}\"\"\"
"""

    pro_rebuttal = models.query_gemini(rebuttal_pro_prompt)
    con_rebuttal = models.query_groq(rebuttal_con_prompt)

    print(f"🔵 PRO Rebuttal:\n{strip_markdown(pro_rebuttal)}\n")
    print(f"🔴 CON Rebuttal:\n{strip_markdown(con_rebuttal)}\n")

    # -----------------------------
    # ROUND 4 — Closing Statements
    # -----------------------------
    print("\n🏁 ROUND 4: Closing Statements\n")

    close_pro_prompt = f"""
You are the PRO side.
Deliver a closing statement:
- Summarize the strongest points
- Quote one weakness from the CON
- End with a decisive conclusion
- Max 5 sentences
"""

    close_con_prompt = f"""
You are the CON side.
Deliver a closing statement:
- Summarize the strongest points
- Quote one weakness from the PRO
- End with a decisive conclusion
- Max 5 sentences
"""

    pro_close = models.query_gemini(close_pro_prompt)
    con_close = models.query_groq(close_con_prompt)

    print(f"🔵 PRO Closing:\n{strip_markdown(pro_close)}\n")
    print(f"🔴 CON Closing:\n{strip_markdown(con_close)}\n")

    # -----------------------------
    # FINAL — Judge's Decision
    # -----------------------------
    print("\n FINAL JUDGMENT\n")

    judge_prompt = f"""
You are a strict, realistic debate judge.
Analyze the debate using criteria:
1) Argument clarity
2) Logical strength
3) Evidence quality
4) Rebuttal effectiveness
5) Closing statement impact
6) Fallacy detection

Debate Topic: {prompt}

PRO Opening:
{pro_arg}

CON Opening:
{con_arg}

PRO Cross:
{pro_cross}

CON Cross:
{con_cross}

PRO Rebuttal:
{pro_rebuttal}

CON Rebuttal:
{con_rebuttal}

PRO Closing:
{pro_close}

CON Closing:
{con_close}

Decide the winner and give a 4–6 sentence justification.
"""

    verdict = models.query_openrouter(judge_prompt)
    print(f"VERDICT:\n{verdict}")


# ==========================================
# MODE 3: CREATIVE ENGINE
# ==========================================
def mode_discussion(prompt):
    print("\n WELCOME TO THE UNIVERSAL CREATIVE ENGINE \n")

    role1 = """
You are the MASTER CREATOR.
- Specializes in imaginative, high-level creativity across all domains:
  • Stories, novels, short stories, scripts
  • Songs, rap, melody, beats, lyrics
  • Painting, visual concepts, composition, color palettes
  • Research and fact-checked essays
  • Captions, slogans, marketing content
  • Product, invention, or design concepts
  • Philosophical and conceptual writing
  • Worldbuilding, lore, game or film ideas
- Produce highly original, cinematic, emotionally and intellectually engaging content.
- Think like the greatest human creators and innovators in history (Leonardo da Vinci, Tolkien, Rahman, Tesla, Picasso, Shakespeare, Steve Jobs, Hans Zimmer, etc.)
"""

    role2 = """
You are the TECHNICAL CRAFTSMAN.
- Convert raw concepts into structured, professional outputs:
  • Songs: Verse, Chorus, Bridge, BPM, flow, rhyme scheme
  • Rap: Punchlines, flow, rhyme, rhythm
  • Story/Book: Chapters, characters, arcs, pacing, dialogue
  • Research: Fact-based expansion, references, citations
  • Captions/Slogans: Concise, catchy, impactful
  • Painting/Design: Style, composition, technique, mood
  • Product/Invention: Features, use-case, specifications
  • Game/Film: Plot, mechanics, scenes, immersion
- Ensure clarity, coherence, rhythm, professional-level output.
"""

    role3 = """
You are the POLISHING DIRECTOR.
- Finalize and perfect the creative piece:
  • Enhance emotional, intellectual, or aesthetic impact
  • Strengthen weak points or unclear parts
  • Improve flow, pacing, or readability
  • Make endings memorable, cinematic, or profound
  • Ensure originality, coherence, and public-ready quality
"""

    # -----------------------------
    # ROUND 1 — MASTER CREATOR 
    # -----------------------------
    print(" ROUND 1: HIGH-LEVEL CREATIVE CONCEPT (Gemini)\n")
    r1_prompt = f"""
{role1}

Create an original concept based on:
"{prompt}"

Include:
- Mood & tone
- Style & format (story, novel, song, rap, painting, caption, slogan, research, book, essay, product concept)
- Key visuals, motifs, or ideas
- Themes or messages
- Emotional or intellectual impact
"""
    r1 = models.query_gemini(r1_prompt)
    print(f"🔵 Gemini (Concept Generation):\n{r1}\n")

    # -----------------------------
    # ROUND 2 — TECHNICAL CRAFTSMAN (Groq)
    # -----------------------------
    print(" ROUND 2: STRUCTURED CREATIVE EXPANSION (Groq)\n")
    r2_prompt = f"""
{role2}

Using this concept:
\"\"\"{r1}\"\"\"

Transform it into a fully developed creative piece:
- Song/rap: full structure, melody, verses, chorus, flow, rhythm
- Story/Book: chapters, characters, arcs, dialogue, pacing
- Research: evidence-based expansion, examples, citations
- Caption/Slogan: concise, catchy, memorable
- Painting/Design: composition, style, lighting, mood
- Product/Invention: features, innovation, usability
- Game/Film: plot, scenes, immersive experience
- Essay/Philosophical writing: structured argument, clarity, insight

Choose the best format for this concept.
Ensure the output is professional, coherent, and engaging.
"""
    r2 = models.query_groq(r2_prompt)
    print(f"🟣 Groq (Technical Expansion):\n{r2}\n")

    # -----------------------------
    # ROUND 3 — POLISHING DIRECTOR (OpenRouter)
    # -----------------------------
    print(" ROUND 3: FINAL POLISH & IMPACT (OpenRouter)\n")
    r3_prompt = f"""
{role3}

Here is the concept and structured draft:
Concept:
\"\"\"{r1}\"\"\"

Draft:
\"\"\"{r2}\"\"\"

Your job:
- Strengthen weak points and unclear parts
- Enhance emotional, intellectual, or aesthetic depth
- Improve musicality, flow, pacing, or readability
- Add cinematic, memorable, or profound endings
- Ensure originality, coherence, and public-ready quality

Produce the FINAL MASTERPIECE that could be published, performed, or presented publicly.
"""
    r3 = models.query_openrouter(r3_prompt)
    print(f"🟢 OpenRouter (Final Masterpiece):\n{r3}\n")

    print("\n UNIVERSAL CREATIVE WORK COMPLETE!\n")


# ==========================================
# QA & AUTO-FIX LOGIC
# ==========================================
def run_qa_loop(project_name, file_structure):
    print("\n QA ENGINEER (Gemini) is reviewing the code...")
    
    for attempt in range(1, 4):
        project_content = ""
        for file_path in file_structure.keys():
            full_path = os.path.join(project_name, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                if any(full_path.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.mp4', '.woff', '.woff2', '.ttf']):
                    continue
                try:
                    with open(full_path, "r") as f:
                        content = f.read()
                        project_content += f"\n--- FILE: {file_path} ---\n{content}\n"
                except Exception:
                    pass
        
        if not project_content:
            print(" No text files found to review.")
            return

        print(f"\n QA Round {attempt}/3...")
        
        qa_prompt = f"""
        You are a Senior QA Engineer.
        Review the following project files for bugs, syntax errors, broken links, and logic issues.
        
        CRITICAL CHECKS:
        1.  **Broken Links**: Does index.html link to the correct CSS/JS files? (e.g., href="style.css" vs href="src/style.css").
        2.  **Missing Files**: Are imported files actually present in the file list?
        3.  **Syntax**: Are there any unclosed tags or syntax errors?
        
        Project Files:
        {project_content[:50000]}
        
        Return ONLY a JSON object with this format:
        {{
            "status": "PASS" or "FAIL",
            "issues": [
                {{"file": "filename", "description": "description of the bug"}}
            ]
        }}
        """
        qa_resp = models.query_gemini(qa_prompt)
        
        # Parse JSON
        clean_json = re.sub(r"```json|```", "", qa_resp).strip()
        try:
            qa_result = json.loads(clean_json)
        except json.JSONDecodeError:
            print(f"⚠️ QA Parse Error. Raw: {qa_resp}")
            break
            
        if qa_result.get("status") == "PASS":
            print("✅ QA PASSED! No critical issues found.")
            break
            
        issues = qa_result.get("issues", [])
        if not issues:
            print("✅ QA PASSED! (No issues listed)")
            break
            
        print(f"❌ QA FAILED. Found {len(issues)} issues. Fixing...")
        
        # Fix Loop
        for issue in issues:
            target_file = issue.get("file")
            bug_desc = issue.get("description")
            
            print(f"  🛠️ Fixing {target_file}: {bug_desc}...")
            
            full_path = os.path.join(project_name, target_file)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    current_content = f.read()
                
                fix_prompt = f"""
                You are a Senior Developer.
                Fix this specific bug identified by QA: "{bug_desc}"
                File: {target_file}
                
                Current Content:
                {current_content}
                
                Return ONLY the COMPLETE fixed code. No markdown.
                """
                fixed_code = models.query_openrouter(fix_prompt)
                clean_fixed_code = re.sub(r"```[\w]*|```", "", fixed_code).strip()
                
                with open(full_path, "w") as f:
                    f.write(clean_fixed_code)
                    
                print(f"     -> Fixed.")
            else:
                print(f"     -> File {target_file} not found.")

# ==========================================
# RUNTIME VERIFICATION & FIX LOGIC
# ==========================================
def run_runtime_verification_loop(project_name):
    print("\n RUNTIME VERIFICATION (Running the code in terminal)...")
    
    # Detect project type
    is_node = os.path.exists(os.path.join(project_name, "package.json"))
    is_python = any(f.endswith(".py") for f in os.listdir(project_name))
    
    start_cmd = []
    
    if is_node:
        print("   -> Detected Node.js project.")
        print("   📦 Installing dependencies (npm install)...")
        try:
            subprocess.run(["npm", "install"], cwd=project_name, check=True, capture_output=True, timeout=60)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"   ⚠️ npm install failed/timed out. Proceeding anyway... Error: {e}")
            
        start_cmd = ["npm", "start"]
        
    elif is_python:
        print("   -> Detected Python project.")
        # Find main file (heuristic: main.py, app.py, or the first python file)
        main_file = "main.py"
        if not os.path.exists(os.path.join(project_name, main_file)):
            py_files = [f for f in os.listdir(project_name) if f.endswith(".py")]
            if py_files:
                main_file = py_files[0]
        
        start_cmd = ["python3", main_file]
    else:
        print("   ⚠️ Unknown project type. Skipping runtime verification.")
        return

    # Runtime Fix Loop (Max 3 attempts)
    for attempt in range(1, 4):
        print(f"\n🔄 Runtime Round {attempt}/3: Executing '{' '.join(start_cmd)}'...")
        
        try:
            # Run the process
            # We use a timeout of 10s. 
            # If it exits with 0 within 10s -> Success (Script finished).
            # If it times out -> Success (Server running).
            # If it exits with != 0 -> Fail (Crash).
            process = subprocess.Popen(
                start_cmd, 
                cwd=project_name, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=10)
                ret_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                print("   ✅ App started and ran for 10s without crashing! (Likely a server)")
                
                # Check for URLs in output
                output = (process.stdout.read() if process.stdout else "") + (process.stderr.read() if process.stderr else "")
                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', output)
                if urls:
                    print(f"\n   🚀 PREVIEW AVAILABLE AT: {urls[0]}")
                    print(f"   (Open this link in your browser to see the app)")
                
                break
                
            if ret_code == 0:
                print("   ✅ App finished successfully (Exit Code 0).")
                break
            
            # If we are here, it crashed
            print(f"   ❌ Runtime Error (Exit Code {ret_code})")
            error_log = (stderr + "\n" + stdout).strip()
            print(f"    Error Log:\n{error_log[-1000:]}") # Last 1000 chars
            
            # Fix it
            print("   🛠️ Attempting to fix runtime error...")
            
            fix_prompt = f"""
            You are a Senior DevOps/Developer.
            The application failed to run.
            Command: {' '.join(start_cmd)}
            Error Log:
            {error_log[-2000:]}
            
            Analyze the error. It might be a missing dependency, a syntax error, or a configuration issue.
            Identify the file that needs fixing and provide the FULL fixed content.
            
            Return ONLY a JSON object with this format:
            {{
                "file": "filename",
                "code": "full fixed code"
            }}
            """
            fix_resp = models.query_openrouter(fix_prompt)
            
            # Parse JSON
            clean_json = re.sub(r"```json|```", "", fix_resp).strip()
            try:
                fix_data = json.loads(clean_json)
                target_file = fix_data["file"]
                fixed_code = fix_data["code"]
                
                full_path = os.path.join(project_name, target_file)
                
                # Ensure directory exists if file is new
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, "w") as f:
                    f.write(fixed_code)
                    
                print(f"   ✅ Updated {target_file} based on runtime error.")
                
            except (json.JSONDecodeError, KeyError):
                print(f"   ⚠️ Failed to parse fix response. Raw: {fix_resp}")
                
        except Exception as e:
            print(f"   ⚠️ Execution failed: {e}")
            break

# ==========================================
# MODE 4: TEAM CODING
# ==========================================
def mode_team_coding(prompt, team_choice="1"):
    print("\n AGENTIC TEAM CODING ACTIVATED\n")
    
    # team_choice is now passed from main menu
    mode_choice = team_choice
    
    if mode_choice == "2":
        # FIX EXISTING PROJECT MODE
        project_path = input("Enter the path to the project folder (e.g., './tara-watch'): ").strip()
        
        if not os.path.exists(project_path):
            print(f"❌ Path '{project_path}' does not exist!")
            return
        
        print(f"\n📂 Reading project from: {project_path}")
        
        # Read all files in the project
        project_files = {}
        for root, dirs, files in os.walk(project_path):
            # Skip node_modules, .git, etc.
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'dist', 'build']]
            
            for file in files:
                # Skip binary files
                if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.mp4', '.woff', '.woff2', '.ttf')):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                
                try:
                    with open(file_path, 'r') as f:
                        project_files[rel_path] = f.read()
                except:
                    pass
        
        print(f"✅ Found {len(project_files)} files to analyze")
        
        # Analyze the project
        print("\n🔍 ARCHITECT (Gemini) is analyzing the project...")
        
        files_summary = "\n".join([f"- {path} ({len(content)} chars)" for path, content in list(project_files.items())[:20]])
        
        analysis_prompt = f"""
        You are a Senior Software Architect analyzing an existing project.
        
        Project files:
        {files_summary}
        
        User request: "{prompt}"
        
        Analyze the project and identify:
        1. What type of project is this? (Web app, Python script, React app, etc.)
        2. What are the main issues or bugs?
        3. What files need to be fixed?
        4. What improvements should be made?
        
        Return a JSON object:
        {{
            "project_type": "description",
            "issues": ["issue1", "issue2"],
            "files_to_fix": ["file1.js", "file2.py"],
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        analysis = models.query_gemini(analysis_prompt)
        clean_json = re.sub(r"```json|```", "", analysis).strip()
        
        try:
            analysis_data = json.loads(clean_json)
            print(f"\n📊 Project Type: {analysis_data.get('project_type', 'Unknown')}")
            print(f"🐛 Issues Found: {len(analysis_data.get('issues', []))}")
            
            for issue in analysis_data.get('issues', [])[:5]:
                print(f"   - {issue}")
        except:
            print(f"⚠️ Could not parse analysis. Proceeding with full project fix...")
            analysis_data = {"files_to_fix": list(project_files.keys())}
        
        # Fix the files
        print("\n🛠️ SENIOR DEV (OpenRouter) is fixing the issues...")
        
        files_to_fix = analysis_data.get('files_to_fix', list(project_files.keys())[:10])
        
        for file_path in files_to_fix:
            if file_path not in project_files:
                continue
                
            print(f"  - Fixing {file_path}...")
            
            current_content = project_files[file_path]
            
            fix_prompt = f"""
            You are a Senior Developer fixing issues in an existing project.
            
            User Request: "{prompt}"
            File: {file_path}
            
            Current Content:
            {current_content[:5000]}
            
            Fix all issues, bugs, and improve the code quality.
            Return ONLY the COMPLETE fixed code. No markdown, no explanations.
            """
            
            fixed_code = models.query_openrouter(fix_prompt)
            clean_fixed = re.sub(r"```[\w]*|```", "", fixed_code).strip()
            
            # Write the fixed file
            full_path = os.path.join(project_path, file_path)
            with open(full_path, 'w') as f:
                f.write(clean_fixed)
        
        print(f"\n✅ Fixed {len(files_to_fix)} files!")
        
        # Run QA on the fixed project
        run_qa_loop(project_path, project_files)
        
        # Run runtime verification
        run_runtime_verification_loop(project_path)
        
        print("\n✅ Project fix complete!")
        return
    
    # CREATE NEW PROJECT MODE (existing code)
    project_name = input("Enter a name for your project (e.g., 'CalculatorApp'): ").strip()

    if not project_name:
        project_name = "GeneratedProject"
    
    # Create project directory
    if not os.path.exists(project_name):
        os.makedirs(project_name)
    
    print(f"\n📂 Created directory: {project_name}")
    
    # 1. ARCHITECT (Gemini)
    print("\n  ARCHITECT (Gemini) is planning the file structure...")
    arch_prompt = f"""
    You are a Senior System Architect & CTO with 25+ years of experience.
    Design a PRODUCTION-READY, SCALABLE file structure for: "{prompt}".
    
    CRITICAL RULES:
    1.  **No Nested Root**: Return keys as relative paths (e.g., "index.html", "style.css"). Do NOT create a top-level folder inside the JSON.
    2.  **Complete Connectivity**: Ensure HTML files link to the correct CSS/JS paths.
        - For simple sites, keep `index.html` and `style.css` in the SAME directory.
    3.  **Modern Stack - SIMPLE APPROACH**:
        - **Web**: Use **Tailwind CSS via CDN ONLY**. NO build process, NO PostCSS, NO npm for simple sites.
        - **Python**: Use Pytest.
    4.  **Minimal Config**: For simple web projects, ONLY include: index.html, style.css (optional), app.js (optional), .gitignore.
        - Do NOT include package.json unless it's a complex Node.js app.
        - Do NOT include build tools for simple landing pages.
    
    Return ONLY a JSON object.
    Example for simple site:
    {{
        "index.html": "<!DOCTYPE html>...",
        "style.css": "/* Optional custom styles */",
        "app.js": "// Optional JS"
    }}
    """
    structure_json = models.query_gemini(arch_prompt)
    
    # Clean and parse JSON
    clean_json = re.sub(r"```json|```", "", structure_json).strip()
    try:
        file_structure = json.loads(clean_json)
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse architecture JSON. Raw output:\n{structure_json}")
        return

    # 2. SCAFFOLDER & CODER (Groq)
    print("\n  SCAFFOLDER & CODER (Groq) are building the project...")
    
    for file_path, description in file_structure.items():
        full_path = os.path.join(project_name, file_path)
        
        # Create subdirectories if needed
        dir_name = os.path.dirname(full_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        print(f"  - Generating {file_path}...")
        
        code_prompt = f"""
        You are a Senior Full Stack Developer (Top 1% Talent).
        
        PROJECT CONTEXT: {prompt}
        FILE TO CREATE: {file_path}
        FILE PURPOSE: {description}
        
        YOUR TASK: Write the COMPLETE, PRODUCTION-READY code for "{file_path}" that is part of the project: "{prompt}".
        
        CRITICAL RULES:
        1.  **STAY ON TOPIC**: The code MUST be relevant to "{prompt}". DO NOT write examples about APIs, Groq, or unrelated topics.
        2.  **COMPLETENESS - NO SKELETONS**: 
            - For HTML landing pages, you MUST include ALL sections:
              * Hero section with headline, description, and CTA button
              * Features/Products section with at least 3 items
              * About/Benefits section
              * Testimonials or social proof (optional but recommended)
              * Contact/CTA section
              * Footer
            - DO NOT generate skeleton HTML with just header/footer
            - Each section must have REAL content, not placeholders
        3.  **IMAGES**: NEVER use local paths. ALWAYS USE: `https://placehold.co/600x400?text=YourText`
        4.  **Robustness**: Handle errors, add comments, use semantic HTML/Python type hinting.
        5.  **No TODOs**: Do not leave "TODO" or "Rest of code here". Write it all.
        6.  **Modern UI (Lovable/Cursor/v0 Style)**: 
            - **MUST USE TAILWIND CSS**: Add `<script src="https://cdn.tailwindcss.com"></script>` in HTML <head>
            - Use **VIBRANT COLORS**: Not gray/white. Use blues, purples, gradients (e.g., `bg-gradient-to-r from-blue-500 to-purple-600`)
            - Use **Google Fonts**: Add Inter or Playfair Display
            - Use **PREMIUM EFFECTS**: backdrop-blur, shadow-2xl, rounded-2xl, hover effects
            - **GENEROUS WHITESPACE**: py-20, px-8, space-y-8
            - **MODERN LAYOUT**: Use flexbox/grid, full-screen hero sections
        7.  **NO INVALID SYNTAX**: 
            - Do NOT use `import` statements in HTML <script> tags
            - Do NOT use JSX or React syntax unless this is explicitly a React project
        8.  **Single File ONLY**: Return ONLY the content for "{file_path}". Do NOT include other files.
        9.  **Connectivity**: If this is HTML, link CSS/JS files correctly (e.g., `<link rel="stylesheet" href="style.css">`).
        
        Return ONLY the code for {file_path}. No explanations, no markdown blocks.
        """
        code = models.query_groq(code_prompt)
        
        # Clean code (remove any markdown code blocks like ```html, ```python, etc.)
        clean_code = re.sub(r"```[\w]*|```", "", code).strip()
        
        # VALIDATION: Check if content is relevant (detect common off-topic patterns)
        irrelevant_patterns = ["groq", "api example", "llama-3", "@groq/cli", "fetch('/api"]
        is_irrelevant = any(pattern in clean_code.lower() for pattern in irrelevant_patterns)
        
        if is_irrelevant:
            print(f"     ⚠️ Detected irrelevant content. Retrying with OpenRouter...")
            # Retry with OpenRouter (more reliable)
            code = models.query_openrouter(code_prompt)
            clean_code = re.sub(r"```[\w]*|```", "", code).strip()
        
        # VALIDATION: Check for invalid import statements in HTML
        if file_path.endswith(".html") and "import " in clean_code and "<script" in clean_code:
            print(f"     ⚠️ Detected invalid import statements in HTML. Removing...")
            # Remove lines with import statements inside script tags
            lines = clean_code.split("\n")
            clean_lines = [line for line in lines if not ("import " in line and "from " in line)]
            clean_code = "\n".join(clean_lines)
        
        # VALIDATION: Ensure Tailwind CDN is present if Tailwind classes are used
        if file_path.endswith(".html"):
            has_tailwind_classes = any(tw_class in clean_code for tw_class in ["class=\"flex", "class=\"grid", "class=\"bg-", "class=\"text-"])
            has_tailwind_cdn = "cdn.tailwindcss.com" in clean_code
            
            if has_tailwind_classes and not has_tailwind_cdn:
                print(f"     ⚠️ Tailwind classes detected but CDN missing. Adding...")
                # Add Tailwind CDN to head
                if "</head>" in clean_code:
                    clean_code = clean_code.replace(
                        "</head>",
                        '    <script src="https://cdn.tailwindcss.com"></script>\n</head>'
                    )
            
            # VALIDATION: Check for missing content in landing pages
            is_landing_page = "landing" in prompt.lower() or "page" in prompt.lower() or "website" in prompt.lower()
            if is_landing_page:
                has_hero = any(keyword in clean_code.lower() for keyword in ["hero", "<h1", "headline"])
                has_features = "feature" in clean_code.lower() or "product" in clean_code.lower()
                file_size = len(clean_code)
                
                if not has_hero or not has_features or file_size < 1500:
                    print(f"     ⚠️ Landing page appears incomplete (size: {file_size} chars). Retrying with OpenRouter...")
                    # Retry with more explicit prompt
                    enhanced_prompt = code_prompt + "\n\nREMINDER: This is a LANDING PAGE. You MUST include: Hero section, Features section, About section, and Footer. Generate COMPLETE HTML, not a skeleton."
                    code = models.query_openrouter(enhanced_prompt)
                    clean_code = re.sub(r"```[\w]*|```", "", code).strip()
        
        # PREVENT CODE LEAKAGE: Remove anything after </html>
        if file_path.endswith(".html"):
            if "</html>" in clean_code:
                clean_code = clean_code.split("</html>")[0] + "</html>"
        
        # Special handling for JSON files to prevent corruption
        if file_path.endswith(".json"):
            try:
                # Try to find the first valid JSON block
                json_match = re.search(r"\{.*\}", clean_code, re.DOTALL)
                if json_match:
                    potential_json = json_match.group(0)
                    json.loads(potential_json) # Validate
                    clean_code = potential_json
            except:
                pass # If validation fails, write as is (QA might fix it)
        
        # Skip if it's just a directory entry (ends with / or no extension)
        if file_path.endswith("/") or "." not in os.path.basename(file_path):
            os.makedirs(full_path, exist_ok=True)
            continue
            
        with open(full_path, "w") as f:
            f.write(clean_code)
            
    print(f"\n✅ Project '{project_name}' built successfully!")
    
    # 3. QA & AUTO-FIX LOOP
    run_qa_loop(project_name, file_structure)
    
    # 4. RUNTIME VERIFICATION LOOP
    run_runtime_verification_loop(project_name)
    
    # 5. INTERACTIVE FIX LOOP (OpenRouter)
    while True:
        print("\n------------------------------------------------")
        user_input = input(" Senior Dev Mode (e.g., 'Fix bug in main.py', 'Exit'): ")
        
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # Simple parsing to find file name
        target_file = None
        for file_path in file_structure.keys():
            if file_path in user_input:
                target_file = file_path
                break
        
        if target_file:
            full_path = os.path.join(project_name, target_file)
            if os.path.exists(full_path):
                with open(full_path, "r") as f:
                    current_content = f.read()
                
                print(f"\n🐞 DEBUGGER (OpenRouter) is analyzing {target_file}...")
                
                debug_prompt = f"""
                You are a Senior Developer with 20+ years of experience.
                User Request: "{user_input}"
                
                Current File Content ({target_file}):
                {current_content}
                
                Return the COMPLETE fixed code for this file.
                Return ONLY the code. No markdown.
                """
                fixed_code = models.query_openrouter(debug_prompt)
                clean_fixed_code = re.sub(r"```[\w]*|```", "", fixed_code).strip()
                
                with open(full_path, "w") as f:
                    f.write(clean_fixed_code)
                    
                print(f"✅ Updated {target_file}")
            else:
                print(f"⚠️ File {target_file} not found locally.")
        else:
            print("⚠️ Could not identify which file to fix. Please mention the filename exactly.")

# ==========================================
# MODE 5: WEIGHTED VOTING
# ==========================================
def mode_voting(prompt):
    print("\n  Collecting responses for voting...\n")
    r1 = models.query_gemini(prompt)
    r2 = models.query_groq(prompt)
    r3 = models.query_openrouter(prompt)
    
    print("  Judge is scoring the answers...\n")
    
    score_prompt = f"""
    Analyze these 3 answers.
    1. Rate them 0-10 based on accuracy and helpfulness.
    2. Write a single paragraph "Judge's Perspective" that synthesizes the best insights from all three answers into a final conclusion.

    Return ONLY a JSON object with this exact format:
    {{
        "scores": {{"gemini": <int>, "groq": <int>, "openrouter": <int>}},
        "judge_perspective": "<single paragraph synthesis of the topic based on all answers>"
    }}
    
    Prompt: {prompt}
    
    Answer 1 (Gemini): {r1[:1000]}...
    Answer 2 (Groq): {r2[:1000]}...
    Answer 3 (OpenRouter): {r3[:1000]}...
    """
    scores_json = models.query_gemini(score_prompt)
    
    import json
    import re

    # Clean up the response (remove markdown code blocks if present)
    clean_json = re.sub(r"```json|```", "", scores_json).strip()
    
    try:
        data = json.loads(clean_json)
        scores = data["scores"]
        perspective = data["judge_perspective"]
        
        # Find winner
        winner_key = max(scores, key=scores.get)
        print(f"\n🏆 WINNER: {winner_key.upper()} (Score: {scores[winner_key]}/10)")
        
        # Map keys to responses to show the winner's answer
        responses = {
            "gemini": r1,
            "groq": r2,
            "openrouter": r3
        }
        
        print(f"\n  {winner_key.upper()}'S ANSWER:\n{strip_markdown(responses.get(winner_key, 'Error retrieving answer'))}")
        
        print(f"\n JUDGE'S PERSPECTIVE:\n{strip_markdown(perspective)}")
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"\n⚠️ Could not parse judge output. Raw output:\n{scores_json}\nError: {e}")

# ==========================================
# MAIN MENU
# ==========================================
def main():
    while True:
        print("\n=================================")
        print("   🤖 MULTI-LLM COLLABORATION    ")
        print("=================================")
        print("1. Consensus Builder")
        print("2. Debate Mode")
        print("3. Discussion Mode (Creative)")
        print("4. Team Coding")
        print("5. Weighted Voting")
        print("6. Exit")
        
        choice = input("\nSelect a mode (1-6): ")
        
        if choice == '6':
            break
        
        # Special handling for Team Coding mode
        if choice == '4':
            print("\n TEAM CODING MODE")
            print("1. Create a new project from scratch")
            print("2. Fix an existing project")
            team_choice = input("\nSelect (1 or 2): ").strip()
            
            if team_choice == "2":
                prompt = input("Describe what to fix (e.g., 'Fix all CSS issues', 'Debug login bug'): ")
            else:
                prompt = input("Describe your project (e.g., 'Create a luxury watch landing page'): ")
            
            mode_team_coding(prompt, team_choice)
        else:
            prompt = input("Enter your topic/problem: ")
            
            if choice == '1':
                mode_consensus(prompt)
            elif choice == '2':
                mode_debate(prompt)
            elif choice == '3':
                mode_discussion(prompt)
            elif choice == '5':
                mode_voting(prompt)
            else:
                print("Invalid choice!")
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
