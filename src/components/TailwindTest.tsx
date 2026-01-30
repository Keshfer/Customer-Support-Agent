/**
 * TailwindTest Component
 * 
 * Test page to verify all Tailwind dark theme colors match the design.
 * This component displays all color variants from the color palette:
 * - Background colors (dark theme)
 * - Agent message colors (light grey)
 * - User message colors (orange)
 * - Header colors (grey tones)
 * - Text colors
 * 
 * Usage: Import and render this component to visually verify color palette
 */
export default function TailwindTest() {
	return (
		<div className="min-h-screen bg-background p-8">
			<h1 className="text-3xl font-bold mb-8 text-text-primary">
				Tailwind Dark Theme Color Palette Test
			</h1>
			
			{/* Background Colors Section */}
			<section className="mb-8">
				<h2 className="text-2xl font-semibold mb-4 text-text-primary">Background Colors</h2>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div className="p-6 bg-background border-2 border-white rounded-lg">
						<p className="text-text-primary font-semibold">background (DEFAULT)</p>
						<p className="text-text-secondary text-sm">#1a1a1a - Main dark background</p>
					</div>
					<div className="p-6 bg-background-dark border-2 border-white rounded-lg">
						<p className="text-text-primary font-semibold">background-dark</p>
						<p className="text-text-secondary text-sm">#0f0f0f - Darker variant</p>
					</div>
				</div>
			</section>

			{/* Agent Message Colors Section */}
			<section className="mb-8">
				<h2 className="text-2xl font-semibold mb-4 text-text-primary">Agent Message Colors</h2>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div className="p-6 bg-agent border-2 border-gray-600 rounded-lg">
						<p className="text-agent-text font-semibold">agent (DEFAULT)</p>
						<p className="text-gray-600 text-sm">#e5e5e5 - Main agent bubble</p>
					</div>
					<div className="p-6 bg-agent-light border-2 border-gray-600 rounded-lg">
						<p className="text-agent-text font-semibold">agent-light</p>
						<p className="text-gray-600 text-sm">#54cffd - Lighter variant</p>
					</div>
					<div className="p-6 bg-agent border-2 border-gray-600 rounded-lg">
						<p className="text-agent-text font-semibold">Agent Message Example</p>
						<p className="text-agent-text text-sm">This is how agent messages will look</p>
					</div>
				</div>
			</section>

			{/* User Message Colors Section */}
			<section className="mb-8">
				<h2 className="text-2xl font-semibold mb-4 text-text-primary">User Message Colors</h2>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div className="p-6 bg-user border-2 border-white rounded-lg">
						<p className="text-user-text font-semibold">user (DEFAULT)</p>
						<p className="text-user-text/80 text-sm">#ff6b35 - Main user bubble</p>
					</div>
					<div className="p-6 bg-user-dark border-2 border-white rounded-lg">
						<p className="text-user-text font-semibold">user-dark</p>
						<p className="text-user-text/80 text-sm">#e55a2b - Darker variant</p>
					</div>
					<div className="p-6 bg-user border-2 border-white rounded-lg">
						<p className="text-user-text font-semibold">User Message Example</p>
						<p className="text-user-text text-sm">This is how user messages will look</p>
					</div>
				</div>
			</section>

			{/* Header Colors Section */}
			<section className="mb-8">
				<h2 className="text-2xl font-semibold mb-4 text-text-primary">Header Colors</h2>
				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div className="p-6 bg-header border-2 border-white rounded-lg">
						<p className="text-header-text font-semibold">header (DEFAULT)</p>
						<p className="text-header-text/80 text-sm">#2d2d2d - Main header background</p>
					</div>
					<div className="p-6 bg-header-light border-2 border-white rounded-lg">
						<p className="text-header-text font-semibold">header-light</p>
						<p className="text-header-text/80 text-sm">#3d3d3d - Lighter variant</p>
					</div>
				</div>
			</section>

			{/* Text Colors Section */}
			<section className="mb-8">
				<h2 className="text-2xl font-semibold mb-4 text-text-primary">Text Colors</h2>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
					<div className="p-6 bg-background border-2 border-white rounded-lg">
						<p className="text-text-primary font-semibold">text-primary</p>
						<p className="text-text-primary text-sm">#ffffff - Primary text (white)</p>
					</div>
					<div className="p-6 bg-background border-2 border-white rounded-lg">
						<p className="text-text-secondary font-semibold">text-secondary</p>
						<p className="text-text-secondary text-sm">#a0a0a0 - Secondary text (grey)</p>
					</div>
					<div className="p-6 bg-background border-2 border-white rounded-lg">
						<p className="text-text-muted font-semibold">text-muted</p>
						<p className="text-text-muted text-sm">#666666 - Muted text</p>
					</div>
				</div>
			</section>

			{/* Visual Preview Section */}
			<section className="mb-8">
				<h2 className="text-2xl font-semibold mb-4 text-text-primary">Visual Preview</h2>
				<div className="bg-background-dark p-6 rounded-lg border-2 border-white">
					{/* Simulated chat interface */}
					<div className="space-y-4">
						{/* Agent message */}
						<div className="flex items-start gap-3">
							<div className="w-8 h-8 rounded-full bg-agent flex items-center justify-center">
								<span className="text-agent-text text-xs font-bold">A</span>
							</div>
							<div className="bg-agent rounded-lg px-4 py-2 max-w-md">
								<p className="text-agent-text text-sm">This is an agent message</p>
								<p className="text-gray-500 text-xs mt-1">10:30 AM</p>
							</div>
						</div>
						
						{/* User message */}
						<div className="flex items-start gap-3 justify-end">
							<div className="bg-user rounded-lg px-4 py-2 max-w-md">
								<p className="text-user-text text-sm">This is a user message</p>
								<p className="text-user-text/80 text-xs mt-1">10:31 AM</p>
							</div>
						</div>
					</div>
				</div>
			</section>
		</div>
	)
}