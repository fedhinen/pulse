<script lang="ts">
	import { page} from '$app/state';
	import { resolve } from '$app/paths';

	let { children } = $props();

	const links: { href: string; label: string }[] = [
		{ href: '/app/handler', label: 'Handlers' },
		{ href: '/app/keys', label: 'API Keys' }
	];
</script>

<div class="min-h-screen flex flex-col">
	<header class="border-b border-zinc-800">
		<div class="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
			<div class="flex items-center gap-8">
				<a href={resolve('/app')} class="text-lg font-bold tracking-tighter no-underline hover:no-underline">
					PULSE
				</a>
				<nav class="flex gap-6">
						<a
							href={resolve('/app/handler')}
							class="text-sm font-medium transition-colors no-underline hover:text-white
                            {page.url.pathname.startsWith('/app/handler') ? 'text-white' : 'text-zinc-500'}"
						>
							Handlers
						</a>
                        <a
                            href={resolve('/app/keys')}
                            class="text-sm font-medium transition-colors no-underline hover:text-white
                            {page.url.pathname.startsWith('/app/keys') ? 'text-white' : 'text-zinc-500'}"
                        >
                            API Keys
                        </a>
				</nav>
			</div>
			<div class="flex items-center gap-4">
                <!-- User profile or logout could go here -->
			</div>
		</div>
	</header>

	<main class="flex-1 max-w-5xl mx-auto w-full px-6 py-12">
		{@render children()}
	</main>
</div>
