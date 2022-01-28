from fastapi import APIRouter
from pydantic import BaseModel, Field
from api.bukkit.bukkit_manager import BukkitManager

router = APIRouter(
    prefix="/api/servers",
    responses={404: {"description": "Not found"}},
)

bukkit_manager = BukkitManager


class ServerCreationData(BaseModel):
    name: str = Field(..., title="Display name of the server")
    type: str = Field(..., title="Server type to install",
                      description="The type of server that should be installed."
                                  "\n\nNormal Server: minecraft"
                                  "\n\nSpigot: spigot"
                                  "\n\nCraftbukkit: craftbukkit")
    version: str = Field(..., title="Server version to install",
                         description="The Minecraft version of this server."
                                     "\n\nFormat: 1.x.x")
    seed: str = Field(..., title="Seed for the world generator")
    gamemode: str = Field(..., title="Gamemode for the server",
                          description="One of [adventure, creative, survival, spectator]")
    leveltype: str = Field(..., title="Leveltype for the world",
                           description="One of [default, flat, largebiomes, amplified]")

    class Config:
        schema_extra = {
            "example": {
                "name": "My Minecraft Server",
                "type": "minecraft",
                "version": "1.18.0",
                "seed": "MySeed",
                "gamemode": "survival",
                "leveltype": "default"
            }
        }


class ServerCreationResponse(BaseModel):
    id: int = Field(..., title="Unique server ID given by mc-server-manager",
                    description="A 4-digit server ID needed to communicate with this server instance through the API."
                                "\n\nWill be 0 if the server couldn't be created.")
    message: str = Field(..., title="The message the server will respond with",
                         description="Will say something like 'Server created successfully!' if there was no error."
                                     "\n\nIf an error occurred, will say something like 'Server creation failed!'.")
    error: str | None = Field(None, title="The error message if something went wrong.",
                              description="Will give the error why creating a new server failed."
                                          "\n\nEmpty if there was no error.")

    class Config:
        schema_extra = {
            "example": {
                "id": 1234,
                "message": "Server created successfully!",
                "error": ""
            }

        }


class ServerStatusResponse(BaseModel):
    status: str = Field(..., title="Status of the server",
                        description="One of [stopped, starting, running, stopping]")

    class Config:
        schema_extra = {
            "example": {
                "status": "running"
            }
        }


@router.post("/", response_model=ServerCreationResponse, responses={
    200: {
        "description": "A new server was successfully created",
    }
})
def create_server(request: ServerCreationData):
    """
    Create a new server with the given data
    """
    print(request)
    return {
        "id": 1,
        "message": "Server created successfully!"
    }


@router.get("/{server_id}/status", response_model=ServerStatusResponse)
def get_server_status(server_id: int):
    """
    Get the status of the server with the given ID
    """
    return {
        "status": "running"
    }


@router.get("/{server_id}/properties")
def get_minecraft_properties(server_id: int):
    return
