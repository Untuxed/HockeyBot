from services.discordStuff import *
from services.firebaseStuff import *

@tree.command(
    name='syncdb',
    description='Syncs the dev collection with the actual season collection',
    guild=GUILD_ID
)
async def syncdb(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        # Hardcode the collection names
        season_collection_name = 'voodoo_lovechild_baierl_e1_spring_2024'
        dev_collection_name = 'voodoo_lovechild_baierl_e1_spring_2024_dev'

        # Clear out the dev collection
        dev_collection_ref = db.collection(dev_collection_name)
        dev_docs = dev_collection_ref.stream()
        for doc in dev_docs:
            doc.reference.delete()

        # Get all documents from the season collection
        season_collection_ref = db.collection(season_collection_name)
        season_docs = season_collection_ref.stream()

        # Write each document to the dev collection
        for doc in season_docs:
            dev_doc_ref = db.collection(dev_collection_name).document(doc.id)
            dev_doc_ref.set(doc.to_dict())

            # Get subcollections of the document
            subcollections = doc.reference.collections()
            for subcollection in subcollections:
                subcollection_docs = subcollection.stream()

                # Write each document in the subcollection to the dev collection
                for sub_doc in subcollection_docs:
                    dev_sub_doc_ref = dev_doc_ref.collection(subcollection.id).document(sub_doc.id)
                    dev_sub_doc_ref.set(sub_doc.to_dict())

        await interaction.followup.send(content='Sync complete!', ephemeral=True)
    except Exception as e:
        print(f'Error syncing collections: {e}')
        await interaction.followup.send(content='An error occurred while syncing the collections.', ephemeral=True)