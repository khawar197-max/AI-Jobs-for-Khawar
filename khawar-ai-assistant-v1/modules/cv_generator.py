from .ai import AIClient

def _profile_text(profile):
    return str(profile)

def build_tailored_cv(profile, opportunity):
    ai = AIClient()
    system = """
You are an expert international CV writer. Create a truthful, ATS-friendly CV
for the opportunity. Never invent employers, degrees, dates, publications,
certifications, software skills, achievements, or metrics.

Use this structure:
NAME
PROFESSIONAL SUMMARY
CORE SKILLS
PROFESSIONAL EXPERIENCE
EDUCATION
PROJECTS
CERTIFICATIONS / TRAINING
ADDITIONAL INFORMATION

Prioritize relevant experience and skills. Keep it concise and suitable for
international employers/universities.
"""
    user = f"""
Candidate:
{_profile_text(profile)}

Target opportunity:
{opportunity}

Write the complete tailored CV.
"""
    return ai.chat(system, user, temperature=0.2)

def build_cover_letter(profile, opportunity):
    ai = AIClient()
    system = """
Write a professional, concise application letter based only on the supplied
candidate profile and opportunity. Do not invent facts. Avoid generic hype.
For PhD/research applications, emphasize research interests and fit without
claiming publications or experience that is not provided.
"""
    user = f"""
Candidate:
{_profile_text(profile)}

Opportunity:
{opportunity}

Write the final cover letter.
"""
    return ai.chat(system, user, temperature=0.3)
