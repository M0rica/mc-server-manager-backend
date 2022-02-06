from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.server_manager import ServerManager
from api.minecraft_server_versions import AvailableMinecraftServerVersions

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)

server_versions = AvailableMinecraftServerVersions()


class AvailableVersionsResponse(BaseModel):
    versions: list = Field(..., title="Supported Minecraft server versions",
                           description="A list containing all supported minecraft server versions")

    class Config:
        schema_extra = {
            "example":
                ["1.18.1, 1.18, 1.17.1", "1.16.2-pre3"]
        }


@router.get("/available_versions", response_model=AvailableVersionsResponse)
def get_available_versions():
    """
    Get all supported minecraft server versions
    """
    return {
        "versions": list(server_versions.available_versions.keys())
    }


server_router = APIRouter(
    prefix="/api/servers",
    responses={404: {"description": "Not found"}},
)

server_manager = ServerManager(server_versions)


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
    seed: Union[str, None] = Field(None, title="Seed for the world generator")
    gamemode: str = Field(..., title="Gamemode for the server",
                          description="One of [adventure, creative, survival, spectator]")
    leveltype: str = Field(..., title="Leveltype for the world",
                           description="One of [default, flat, largebiomes, amplified]")

    class Config:
        schema_extra = {
            "example": {
                "name": "My Minecraft Server",
                "type": "minecraft",
                "version": "1.18.1",
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
    error: Union[str, None] = Field(None, title="The error message if something went wrong.",
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
    data: dict = Field(..., title="Complete server data",
                        description="Returns a dict with all of this server's data")

    class Config:
        schema_extra = {
            "example": {
                "status": "running"
            }
        }


class AllServerStatusResponse(BaseModel):
    data: dict = Field(..., title="Dict with complete server data of each server",
                       description="A dict with complete server data of every server with server ids as keys")

@server_router.post("/", response_model=ServerCreationResponse, responses={
    200: {
        "description": "A new server was successfully created",
    }
})
def create_server(request: ServerCreationData):
    """
    Create a new server with the given data
    """
    print(request)
    id = server_manager.create_server(request.dict())
    return {
        "id": id,
        "message": "Server created successfully!"
    }


@server_router.get("/", response_model=AllServerStatusResponse)
def get_server_data():
    return {
        "data": server_manager.get_all_server_data()
    }


@server_router.get("/{server_id}", response_model=ServerStatusResponse)
def get_server_status(server_id: int):
    """
    Get the status of the server with the given ID
    """
    return {
        "data": server_manager.get_server_data(server_id)
    }
