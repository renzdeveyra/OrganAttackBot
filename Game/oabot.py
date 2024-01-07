import discord

import game
from utils import generate_attack_embeds, display_organs

game_key_ref = ''
games_registry = {}

def activate(client, config, handler, logging_debug):
    @client.event
    async def on_ready():
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')

    players_list = {}  # would be open to players joining until game starts

    @client.tree.command(name='join', description='Join a game.')
    async def join(interaction: discord.Interaction):
        user_mention = interaction.user.mention
        user_name = interaction.user.name
        if user_name in players_list:
            print("this")
            await interaction.response.send_message(f"Last time I checked, you already joined {user_name}...")
            return
        # elif user in games_registry[game_key_ref]['players']:
        #     await interaction.response.send_message(f"U okay, {user}?\nYou're literally playing right now (◕︿◕✿)")
        #     return
        if len(players_list) == 6:
            await interaction.response.send_message(f"There's already 6 of you! (,,>﹏<,,)\n"
                                                    f'Type `/players` to see for yourself (¬_¬")')
            return
        else:
            players_list[user_mention] = user_name
            print(f"Added {user_name} as {user_mention}")
            await interaction.response.send_message(f"Hello, {user_mention}\n"
                                                    "You have joined the game! (✿◠‿◠)")

    @client.tree.command(name='players-list', description='View the players in your lobby.')
    async def players(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.mention}\n"
                                                f"These are the players\n(☞ ͡° ͜ʖ ͡°)☞  {', '.join(players_list)}")

    class Menu(discord.ui.View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label="Play Instant", style=discord.ButtonStyle.danger, row=0, emoji="🔥")
        async def instant_play_button(self, interaction: discord.Interaction, Button: discord.ui.Button):
            await interaction.response.send_message("Instant Card Played!")

    class PlayCard(discord.ui.Select):
        def __init__(self):
            options = []
            super().__init__(placeholder="Choose your card", min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            Game = games_registry[game_key_ref]['game']
            Game.handle_turn()
            await interaction.response.send_message(f"{self.values} was played! Nice one, {interaction.user.mention}!"
                                                    f"★~(◠‿◕✿)\nNow, it's {Game.turn[0]}'s turn!")

    @client.tree.command(name='start', description="Let's play!")
    async def start(interaction: discord.Interaction):
        global game_key_ref
        user = interaction.user.mention
        # if user in games_registry[game_key_ref]['players']:
        #     await interaction.response.send_message(f"U okay, {user}?\nYou're literally playing right now (◕︿◕✿)")
        if len(players_list) < 2:
            await interaction.response.send_message("fr? (ಥ ͜ʖಥ)")
        else:
            game_key = f"{user}'s_game_{len(games_registry) + 1}"
            game_key_ref = game_key
            print(f"Game key: {game_key}")
            Game = game.Game(players_list)
            games_registry[game_key] = {'game': Game, 'players': players_list, 'started': True}
            Game.start()
            players_list.clear()
            organs_distribution = display_organs(Game.hands['attack'])

            await interaction.response.send_message(
                f"🩷 **Game Start!!** 🩷\n\nGood luck! (づ｡◕‿‿◕｡)づ\n\n {organs_distribution}\r"
                "Here are your **Organs**!\nTake good care of them! (◡‿◡✿)"
            )
            print(f"Turn order: {Game.turn}")

    @client.tree.command(name='attack', description='View your Hand hidden from other players and play them!')
    async def attack(interaction: discord.Interaction):
        user = interaction.user.name
        Game = games_registry[game_key_ref]['game']
        embeds = generate_attack_embeds(Game, user)
        cards_select = PlayCard()

        view = Menu()

        if Game.turn[0] == user:
            for i in range(Game.attack_hand_count):
                cards_select.options.append(
                    discord.SelectOption(label=Game.attack_assignments[user].get_card(i).name,
                                         description=Game.attack_assignments[user].get_card(i).card_type)
                )

            view = Menu.add_item(Menu(), cards_select)
        await interaction.response.send_message(view=view, embeds=embeds, ephemeral=True)

    client.run(config, log_handler=handler, log_level=logging_debug)
