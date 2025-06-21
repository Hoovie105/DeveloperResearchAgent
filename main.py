from dotenv import load_dotenv
from src.workflow import Workflow
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Request
import uvicorn

load_dotenv()


class AgentQuery(BaseModel):
    query: str


def main():
    workflow = Workflow()
    print("Developer Tools Research Agent")

    while True:
        query = input("\n🔍 Developer Tools Query: ").strip()
        if query.lower() in {"quit", "exit"}:
            break

        if query:
            result = workflow.run(query)
            print(f"\n📊 Results for: {query}")
            print("=" * 60)

            for i, company in enumerate(result.companies, 1):
                print(f"\n{i}. 🏢 {company.name}")
                print(f"   🌐 Website: {company.website}")
                print(f"   💰 Pricing: {company.pricing_model}")
                print(f"   📖 Open Source: {company.is_open_source}")

                if company.tech_stack:
                    print(f"   🛠️  Tech Stack: {', '.join(company.tech_stack[:5])}")

                if company.language_support:
                    print(
                        f"   💻 Language Support: {', '.join(company.language_support[:5])}"
                    )

                if company.api_available is not None:
                    api_status = (
                        "✅ Available" if company.api_available else "❌ Not Available"
                    )
                    print(f"   🔌 API: {api_status}")

                if company.integration_capabilities:
                    print(
                        f"   🔗 Integrations: {', '.join(company.integration_capabilities[:4])}"
                    )

                if company.description and company.description != "Analysis failed":
                    print(f"   📝 Description: {company.description}")

                print()

            if result.analysis:
                print("Developer Recommendations: ")
                print("-" * 40)
                print(result.analysis)


def create_app():
    app = FastAPI()
    # Allow CORS for local frontend.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/api/agent")
    async def agent_endpoint(payload: AgentQuery, request: Request):
        query = payload.query
        workflow = Workflow()
        try:
            result = workflow.run(query)
            # Prepare companies as list of dicts if available
            companies = []
            if hasattr(result, 'companies') and result.companies:
                for c in result.companies:
                    companies.append({
                        'name': getattr(c, 'name', None),
                        'website': getattr(c, 'website', None),
                        'pricing_model': getattr(c, 'pricing_model', None),
                        'is_open_source': getattr(c, 'is_open_source', None),
                        'tech_stack': getattr(c, 'tech_stack', None),
                        'language_support': getattr(c, 'language_support', None),
                        'api_available': getattr(c, 'api_available', None),
                        'integration_capabilities': getattr(c, 'integration_capabilities', None),
                        'description': getattr(c, 'description', None),
                    })
            response = {
                'query': query,
                'analysis': getattr(result, 'analysis', None),
                'companies': companies,
            }
        except Exception as e:
            response = {'error': str(e), 'query': query}
        return response

    return app


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Run FastAPI backend
        uvicorn.run("main:create_app", host="0.0.0.0", port=8000, factory=True, reload=True)
    else:
        main()