<script>
	import { resolve } from '$app/paths';
</script>

<div class="py-12">
	<h1 class="text-4xl font-light mb-2">Welcome to Pulse</h1>
	<p class="text-zinc-500 text-lg mb-12">Serverless function management made simple.</p>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		<a href={resolve('/app/handler')} class="group block p-8 border border-zinc-800 hover:border-white transition-colors no-underline bg-zinc-900/20">
			<h3 class="text-xl font-medium mb-2 group-hover:text-white transition-colors">Handlers</h3>
			<p class="text-zinc-500 text-sm">Deploy and manage your serverless functions. Monitor status and execution.</p>
			<div class="mt-6 text-sm font-medium text-white group-hover:underline">Manage Handlers &rarr;</div>
		</a>

		<a href={resolve('/app/keys')} class="group block p-8 border border-zinc-800 hover:border-white transition-colors no-underline bg-zinc-900/20">
			<h3 class="text-xl font-medium mb-2 group-hover:text-white transition-colors">API Keys</h3>
			<p class="text-zinc-500 text-sm">Generate and revoke access keys for your applications securely.</p>
			<div class="mt-6 text-sm font-medium text-white group-hover:underline">Manage Keys &rarr;</div>
		</a>
	</div>
</div>
