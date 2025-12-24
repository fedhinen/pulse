<script>
	import { resolve } from '$app/paths';
</script>

<div class="min-h-screen flex flex-col items-center justify-center text-center px-4">
	<h1 class="text-6xl font-bold tracking-tighter mb-6">PULSE</h1>
	<p class="text-xl text-zinc-500 max-w-lg mb-10">
		A minimalist serverless function platform. Deploy code in seconds.
	</p>
	
	<div class="flex gap-4">
		<a href={resolve('/auth/signin')} class="bg-white text-black px-8 py-3 text-sm font-medium hover:bg-zinc-200 transition-colors no-underline">
			Get Started
		</a>
		<a href="https://github.com/fedhinen/pulse" target="_blank" class="bg-transparent text-white border border-zinc-800 px-8 py-3 text-sm font-medium hover:border-white transition-colors no-underline">
			GitHub
		</a>
	</div>
</div>
