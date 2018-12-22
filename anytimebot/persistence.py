class Anytime:
    partecipants = []

    def __init__(self, size):
        # TODO check size is power of 2
        self.size = size

    async def addParticipant(self, user, context):
        self.partecipants.append(user)
        if len(self.partecipants) == self.size:
            await self.startTournament(context)

    async def startTournament(self, context):
        await context.message.guild.create_text_channel('cool-channel')
        print(f'Starting a tournament with users: {self.partecipants}')
