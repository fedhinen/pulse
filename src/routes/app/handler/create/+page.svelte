<script>
	import { createHandler } from '$lib/modules/handler/handler.remote';
	import { HandlerCreatePreflightSchema } from '$lib/modules/handler/handler.schemas';
	import { resolve } from '$app/paths';
</script>

<div class="max-w-2xl mx-auto">
	<div class="mb-8">
		<a href={resolve('/app/handler')} class="text-zinc-500 text-sm hover:text-white mb-4 inline-block">&larr; Back to Handlers</a>
		<h1 class="mb-2">Create Handler</h1>
		<p class="text-zinc-500 text-sm">Deploy a new serverless function</p>
	</div>

	<form {...createHandler.preflight(HandlerCreatePreflightSchema)} enctype="multipart/form-data" class="space-y-6">
		<label>
			<h4>Name</h4>
			<input {...createHandler.fields.name.as('text')} type="text" placeholder="my-handler" />
			<p class="text-xs text-zinc-500 mt-2">Unique identifier for your handler</p>
		</label>
		
		<div class="flex items-center gap-3 p-4 border border-zinc-800 bg-zinc-900/30">
			<input {...createHandler.fields.async.as('checkbox')} type="checkbox" class="w-4 h-4" />
			<div>
				<h4 class="mb-0! text-white!">Async Execution</h4>
				<p class="text-xs text-zinc-500 mt-1">Run this handler in the background</p>
			</div>
		</div>

		<label>
			<h4>Code File</h4>
			<div class="relative">
				<input {...createHandler.fields.file.as('file')} type="file" class="file:mr-4 file:py-2 file:px-4 file:border-0 file:text-xs file:font-medium file:bg-zinc-800 file:text-white hover:file:bg-zinc-700 text-zinc-400" />
			</div>
			<p class="text-xs text-zinc-500 mt-2">Upload your Python script (.py)</p>
		</label>

		{#each createHandler.fields.allIssues() as issue (issue.message)}
			<p class="issue">
				{#each issue.path as path (path)}
					{typeof path === 'number' ? `[${path}]` : `.${path}`}
				{/each}: {issue.message}
			</p>
		{/each}

		<div class="pt-4">
			<button type="submit">Create Handler</button>
		</div>
	</form>
</div>
