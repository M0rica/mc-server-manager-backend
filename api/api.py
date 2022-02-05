from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.server_manager import ServerManager

router = APIRouter(
    prefix="/api",
    responses={404: {"description": "Not found"}},
)


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
    return {
        "versions": list(server_manager.available_versions.keys())
    }


server_router = APIRouter(
    prefix="/api/servers",
    responses={404: {"description": "Not found"}},
)

server_manager = ServerManager()


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
                "type": "spigot",
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


class ServerIDsResponse(BaseModel):
    ids: list = Field(..., title="List of all server IDs",
                      description="Returns a list with all server IDs")

    class Config:
        schema_extra = {
            "example": {
                "ids": [
                    1001, 3425, 1234
                ]
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


@server_router.get("/", response_model=ServerIDsResponse)
def get_server_ids():
    return


@server_router.get("/{server_id}", response_model=ServerStatusResponse)
def get_server_status(server_id: int):
    """
    Get the status of the server with the given ID
    """
    return server_manager.get_server_data(server_id)