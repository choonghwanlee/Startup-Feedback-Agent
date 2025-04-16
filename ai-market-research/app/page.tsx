import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Search,
  BarChart2,
  Target,
  Users,
  Globe,
  DollarSign,
} from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b bg-white">
        <div className="container flex h-16 items-center px-4 md:px-6 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <BarChart2 className="h-5 w-5 text-primary" />
            <span className="text-xl font-semibold">AI Market Research</span>
          </div>
          <nav className="ml-auto flex gap-4">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                Login
              </Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Sign Up</Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 bg-slate-50">
          <div className="container px-4 md:px-6 max-w-7xl mx-auto">
            <div className="flex flex-col items-center space-y-6 text-center">
              <div className="space-y-3">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                  AI Market Research Analyst
                </h1>
                <p className="mx-auto max-w-[700px] text-slate-600 md:text-xl">
                  Get valuable insights for your startup ideas with our
                  AI-powered market research analyst.
                </p>
              </div>
              <div className="space-x-4">
                <Link href="/signup">
                  <Button size="lg" className="px-8">
                    Get Started <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/login">
                  <Button variant="outline" size="lg">
                    Try Demo
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="w-full py-12 md:py-24 bg-white">
          <div className="container px-4 md:px-6 max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold tracking-tight">
                Powerful Market Research Features
              </h2>
              <p className="mt-4 text-lg text-slate-600 max-w-3xl mx-auto">
                Our AI-powered platform provides comprehensive market analysis
                to help you validate and refine your startup ideas.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {/* Feature 1 */}
              <div className="flex flex-col items-start p-6 bg-slate-50 rounded-lg border border-slate-200">
                <div className="rounded-full bg-primary/10 p-3 mb-4">
                  <Search className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Deep Market Research
                </h3>
                <p className="text-slate-600">
                  Leverage web search capabilities to gather real-time market
                  data and trends for your industry.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="flex flex-col items-start p-6 bg-slate-50 rounded-lg border border-slate-200">
                <div className="rounded-full bg-primary/10 p-3 mb-4">
                  <BarChart2 className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Competitive Analysis
                </h3>
                <p className="text-slate-600">
                  Identify key competitors, their strengths, weaknesses, and
                  market positioning to find your edge.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="flex flex-col items-start p-6 bg-slate-50 rounded-lg border border-slate-200">
                <div className="rounded-full bg-primary/10 p-3 mb-4">
                  <Target className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">SWOT Analysis</h3>
                <p className="text-slate-600">
                  Comprehensive evaluation of Strengths, Weaknesses,
                  Opportunities, and Threats for your business idea.
                </p>
              </div>

              {/* Feature 4 */}
              <div className="flex flex-col items-start p-6 bg-slate-50 rounded-lg border border-slate-200">
                <div className="rounded-full bg-primary/10 p-3 mb-4">
                  <Globe className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Go-to-Market Strategy
                </h3>
                <p className="text-slate-600">
                  Develop effective launch strategies, marketing channels, and
                  customer acquisition plans.
                </p>
              </div>

              {/* Feature 5 */}
              <div className="flex flex-col items-start p-6 bg-slate-50 rounded-lg border border-slate-200">
                <div className="rounded-full bg-primary/10 p-3 mb-4">
                  <DollarSign className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Pricing Strategy</h3>
                <p className="text-slate-600">
                  Determine optimal pricing models based on market analysis,
                  competitor pricing, and value perception.
                </p>
              </div>

              {/* Feature 6 */}
              <div className="flex flex-col items-start p-6 bg-slate-50 rounded-lg border border-slate-200">
                <div className="rounded-full bg-primary/10 p-3 mb-4">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Target Audience Insights
                </h3>
                <p className="text-slate-600">
                  Identify ideal customer profiles, market segments, and user
                  personas for your product or service.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full py-12 md:py-24 bg-primary text-primary-foreground">
          <div className="container px-4 md:px-6 max-w-7xl mx-auto">
            <div className="flex flex-col items-center space-y-4 text-center">
              <h2 className="text-3xl font-bold tracking-tight">
                Ready to Validate Your Startup Idea?
              </h2>
              <p className="mx-auto max-w-[700px] text-primary-foreground/80 md:text-lg">
                Get started today and receive AI-powered market insights to help
                your business succeed.
              </p>
              <Link href="/signup">
                <Button size="lg" variant="secondary" className="mt-4">
                  Start Free Analysis
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t bg-slate-50">
        <div className="container flex flex-col md:flex-row items-center justify-between gap-4 py-10 px-4 md:px-6 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <BarChart2 className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium">
              AI Market Research Analyst
            </span>
          </div>
          <p className="text-sm text-slate-500">
            © 2025 AI Market Research. All rights reserved.
          </p>
          <div className="flex gap-4">
            <Link
              href="#"
              className="text-sm text-slate-500 hover:text-slate-900"
            >
              Terms
            </Link>
            <Link
              href="#"
              className="text-sm text-slate-500 hover:text-slate-900"
            >
              Privacy
            </Link>
            <Link
              href="#"
              className="text-sm text-slate-500 hover:text-slate-900"
            >
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
