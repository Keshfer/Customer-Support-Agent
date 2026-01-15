import * as z from 'zod'

const MessageScheme = z.object({
	id:z.string().optional(),
	message:z.string(),
	sender:z.enum(["user", "agent"]),
	timestamp:z.string().optional()
});

const ChatResponseScheme = z.object({
	response: z.string(),
	conversation_id: z.string()
});

const ScrapeResponseScheme = z.object({
	website_id: z.number(),
  	status: z.string(),
  	message: z.string().optional()
});

const WebsiteScheme = z.object({
	id: z.number(),
	url: z.string(),
	title: z.string().optional(),
	scraped_at: z.string().optional(),
	status: z.string()
});

const WebsiteListResponseScheme = z.object({
	websites: z.array(WebsiteScheme)
});

const ContentChunkScheme = z.object({
	id: z.number(),
	website_id: z.number(),
	chunk_text: z.string(),
	chunk_index: z.number(),
	metadata: z.record(z.string(), z.any()).optional(),
	created_at: z.string().optional()
})

const WebsiteChunksResponseScheme = z.object({
	website: WebsiteScheme,
	chunks: z.array(ContentChunkScheme)
})

const ConversationScheme = z.object({
	id: z.string(),
	messages: z.array(MessageScheme),
	created_at: z.string().optional(),
	updated_at: z.string().optional(),
})

const ApiErrorScheme = z.object({
	error: z.string(),
	message: z.string().optional(),
	status: z.number().optional()
})

//Test Types
console.log("=".repeat(50))
console.log("Types Test")
console.log("=".repeat(50))
const validUserMessage = MessageScheme.safeParse({
	id: "123",
	message: "Hello, how are you?",
	sender: "user",
	timestamp: "2026-01-13T12:00:00Z"
});
if (!validUserMessage.success) {
	console.error("X Valid user message test failed:", validUserMessage.error.message);
} else {
	console.log("✓ Valid user message test passed");
}

const validAgentMessage = MessageScheme.safeParse({
	id: "123",
	message: "Hello, how are you?",
	sender: "agent",
	timestamp: "2026-01-13T12:00:00Z"
});
if (!validAgentMessage.success) {
	console.error("X Valid agent message test failed:", validAgentMessage.error.message);
} else {
	console.log("✓ Valid agent message test passed");
}

const invalidSenderVal = MessageScheme.safeParse({
	id: "123",
	message: "Hello, how are you?",
	sender: "invalid",
	timestamp: "2026-01-13T12:00:00Z"
});
if (!invalidSenderVal.success) {
	console.log("✓ Invalid sender value test passed");
} else {
	console.error("X Invalid sender value test failed:", invalidSenderVal.data);
}

const absentOptionalsMessage = MessageScheme.safeParse({
	id: "123",
	message: "Hello, how are you?",
	sender: "user"
});
if (!absentOptionalsMessage.success) {
	console.error("X Absent optionals test failed:", absentOptionalsMessage.error.message);
} else {
	console.log("✓ Absent optionals test passed");
}

const validChatResponse = ChatResponseScheme.safeParse({
	response: "Hello, how are you?",
	conversation_id: "123"
});
if (!validChatResponse.success) {
	console.error("X Valid chat response test failed:", validChatResponse.error.message);
} else {
	console.log("✓ Valid chat response test passed");
}

const invalidChatResponse = ChatResponseScheme.safeParse({
	response: "Hello, how are you?",
	conversation_id: 123
});
if (!invalidChatResponse.success) {
	console.log("✓ Invalid chat response test passed");
} else {
	console.error("X Invalid chat response test failed:", invalidChatResponse.data);
}

const validScrapeResponse = ScrapeResponseScheme.safeParse({
	website_id: 123,
	status: "success",
	message: "Scraped successfully"
});
if (!validScrapeResponse.success) {
	console.error("X Valid scrape response test failed:", validScrapeResponse.error.message);
} else {
	console.log("✓ Valid scrape response test passed");
}

const invalidScrapeResponse = ScrapeResponseScheme.safeParse({
	website_id: null,
	status: null,
	message: null
});
if (!invalidScrapeResponse.success) {
	console.log("✓ Invalid scrape response test passed");
} else {
	console.error("X Invalid scrape response test failed:", invalidScrapeResponse.data);
}

const validWebsite = WebsiteScheme.safeParse({
	id: 123,
	url: "https://example.com",
	title: "Example Website",
	scraped_at: "2026-01-13T12:00:00Z",
	status: "completed",
});
if (!validWebsite.success) {
	console.error("X Valid website test failed:", validWebsite.error.message);
} else {
	console.log("✓ Valid website test passed");
}

const invalidWebsite = WebsiteScheme.safeParse({
	id: null,
	url: null,
	title: null,
	scraped_at: null,
	status: null,
});
if (!invalidWebsite.success) {
	console.log("✓ Invalid website test passed");
} else {
	console.error("X Invalid website test failed:", invalidWebsite.data);
}

const validWebsiteListResponse = WebsiteListResponseScheme.safeParse({
	websites: [
		{
			id: 123,
			url: "https://example.com",
			title: "Example Website",
			scraped_at: "2026-01-13T12:00:00Z",
			status: "completed",
		}
	]
});
if (!validWebsiteListResponse.success) {
	console.error("X Valid website list response test failed:", validWebsiteListResponse.error.message);
} else {
	console.log("✓ Valid website list response test passed");
}

const validApiError = ApiErrorScheme.safeParse({
	error: "Internal Server Error",
	message: "An unexpected error occurred",
	status: 500
});
if (!validApiError.success) {
	console.error("X Valid api error test failed:", validApiError.error.message);
} else {
	console.log("✓ Valid api error test passed");
}