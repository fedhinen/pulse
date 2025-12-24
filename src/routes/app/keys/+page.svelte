<script>
	import { createKey, getKeys } from '$lib/modules/keys/keys.remote';
	import { KeyCreatePreflightSchema } from '$lib/modules/keys/keys.schemas';
</script>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-12">
	<div class="lg:col-span-2">
		<div class="mb-8">
			<h1 class="mb-2">API Keys</h1>
			<p class="text-zinc-500 text-sm">Manage access keys for your applications</p>
		</div>

		<div class="border border-zinc-800">
			<div class="grid grid-cols-12 gap-4 p-4 border-b border-zinc-800 bg-zinc-900/50 text-xs font-medium text-zinc-400 uppercase tracking-wider">
				<div class="col-span-4">Name</div>
				<div class="col-span-8">Prefix</div>
			</div>

			{#await getKeys()}
				<div class="p-8 text-center text-zinc-500">Loading keys...</div>
			{:then keys}
				{#if keys.length === 0}
					<div class="p-8 text-center text-zinc-500">No API keys found.</div>
				{:else}
					{#each keys as { id, name, prefix } (id)}
						<div class="grid grid-cols-12 gap-4 p-4 border-b border-zinc-800 last:border-0 items-center hover:bg-zinc-900/30 transition-colors">
							<div class="col-span-4 font-medium text-white">{name}</div>
							<div class="col-span-8 font-mono text-xs text-zinc-500">{prefix}••••••••••••••••</div>
						</div>
					{/each}
				{/if}
			{/await}
		</div>
	</div>

	<div>
		<div class="bg-zinc-900/30 border border-zinc-800 p-6 sticky top-6">
			<h3 class="text-lg font-medium mb-4">Create New Key</h3>
			
			<form {...createKey.preflight(KeyCreatePreflightSchema)} class="space-y-4">
				<label>
					<h4>Name</h4>
					<input {...createKey.fields.name.as('text')} type="text" placeholder="e.g. Production App" />
				</label>

				<button type="submit" class="w-full">Generate Key</button>
			</form>

			{#each createKey.result as result (result)}
				{#if result?.key}
					<div class="mt-6 p-4 bg-green-900/20 border border-green-900/50">
						<p class="text-green-400 text-xs font-medium uppercase mb-2">Key Generated Successfully</p>
						<p class="text-white font-mono text-sm break-all select-all bg-black/50 p-2 border border-green-900/30">{result.key}</p>
						<p class="text-zinc-500 text-xs mt-2">Copy this key now. You won't be able to see it again.</p>
					</div>
				{:else}
					<div class="mt-6 p-4 bg-red-900/20 border border-red-900/50">
						<p class="text-red-400 text-sm">Error generating key</p>
					</div>
				{/if}
			{/each}
		</div>
	</div>
</div>
