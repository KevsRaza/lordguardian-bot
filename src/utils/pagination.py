"""
Pagination utility for Discord embeds
"""
import discord
from discord.ext import commands
from typing import List, Optional
import asyncio


class Paginator:
    """Simple paginator for embeds"""
    
    def __init__(
        self,
        ctx: commands.Context,
        pages: List[discord.Embed],
        timeout: float = 60.0
    ):
        self.ctx = ctx
        self.pages = pages
        self.timeout = timeout
        self.current_page = 0
        self.message: Optional[discord.Message] = None
        
        # Emojis for navigation
        self.first = "⏮️"
        self.previous = "◀️"
        self.next = "▶️"
        self.last = "⏭️"
        self.stop = "⏹️"
        
        self.emojis = [self.first, self.previous, self.stop, self.next, self.last]
    
    async def start(self):
        """Start the paginator"""
        if not self.pages:
            await self.ctx.send("No pages to display.")
            return
        
        # Update first page footer
        self.pages[0].set_footer(text=f"Page 1/{len(self.pages)}")
        self.message = await self.ctx.send(embed=self.pages[0])
        
        # Only add reactions if more than 1 page
        if len(self.pages) > 1:
            for emoji in self.emojis:
                await self.message.add_reaction(emoji)
            
            # Start listening for reactions
            await self._paginate()
    
    async def _paginate(self):
        """Handle pagination reactions"""
        def check(reaction, user):
            return (
                user == self.ctx.author
                and str(reaction.emoji) in self.emojis
                and reaction.message.id == self.message.id
            )
        
        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    "reaction_add",
                    timeout=self.timeout,
                    check=check
                )
                
                # Handle reaction
                emoji = str(reaction.emoji)
                
                if emoji == self.first:
                    self.current_page = 0
                elif emoji == self.previous:
                    if self.current_page > 0:
                        self.current_page -= 1
                elif emoji == self.next:
                    if self.current_page < len(self.pages) - 1:
                        self.current_page += 1
                elif emoji == self.last:
                    self.current_page = len(self.pages) - 1
                elif emoji == self.stop:
                    await self.message.delete()
                    return
                
                # Update embed
                page = self.pages[self.current_page]
                page.set_footer(text=f"Page {self.current_page + 1}/{len(self.pages)}")
                await self.message.edit(embed=page)
                
                # Remove user's reaction
                try:
                    await self.message.remove_reaction(reaction, user)
                except discord.HTTPException:
                    pass
            
            except asyncio.TimeoutError:
                # Remove all reactions on timeout
                try:
                    await self.message.clear_reactions()
                except discord.HTTPException:
                    pass
                break


class SimplePaginator:
    """Text-based paginator"""
    
    def __init__(
        self,
        ctx: commands.Context,
        entries: List[str],
        per_page: int = 10,
        title: str = "Paginated Results",
        color: discord.Color = discord.Color.blurple()
    ):
        self.ctx = ctx
        self.entries = entries
        self.per_page = per_page
        self.title = title
        self.color = color
        
        # Create pages
        self.pages = self._create_pages()
    
    def _create_pages(self) -> List[discord.Embed]:
        """Create embed pages from entries"""
        pages = []
        total_pages = (len(self.entries) + self.per_page - 1) // self.per_page
        
        for page_num in range(total_pages):
            start = page_num * self.per_page
            end = start + self.per_page
            page_entries = self.entries[start:end]
            
            embed = discord.Embed(
                title=self.title,
                description="\n".join(page_entries),
                color=self.color
            )
            embed.set_footer(text=f"Page {page_num + 1}/{total_pages}")
            pages.append(embed)
        
        return pages
    
    async def start(self):
        """Start pagination"""
        paginator = Paginator(self.ctx, self.pages)
        await paginator.start()


def create_embed_pages(
    items: List[str],
    title: str,
    per_page: int = 10,
    color: discord.Color = discord.Color.blurple()
) -> List[discord.Embed]:
    """
    Helper function to create embed pages from a list of items
    """
    pages = []
    total_pages = (len(items) + per_page - 1) // per_page
    
    for page_num in range(total_pages):
        start = page_num * per_page
        end = start + per_page
        page_items = items[start:end]
        
        embed = discord.Embed(
            title=title,
            description="\n".join(page_items),
            color=color
        )
        embed.set_footer(text=f"Page {page_num + 1}/{total_pages} • {len(items)} total items")
        pages.append(embed)
    
    return pages