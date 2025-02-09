#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.

from typing import List, Optional

from idb.grpc.idb_pb2 import DebugServerRequest, DebugServerResponse
from idb.grpc.stream import Stream, join_streams
from idb.grpc.types import CompanionClient


async def _unary(
    client: CompanionClient, request: DebugServerRequest
) -> DebugServerResponse:
    async with client.stub.debugserver.open() as stream:
        await stream.send_message(request)
        await stream.end()
        return await stream.recv_message()


async def debugserver_start(client: CompanionClient, bundle_id: str) -> List[str]:
    response = await _unary(
        client=client,
        request=DebugServerRequest(start=DebugServerRequest.Start(bundle_id=bundle_id)),
    )
    return response.status.lldb_bootstrap_commands


async def debugserver_stop(client: CompanionClient) -> None:
    await _unary(
        client=client, request=DebugServerRequest(stop=DebugServerRequest.Stop())
    )


async def debugserver_status(client: CompanionClient) -> Optional[List[str]]:
    response = await _unary(
        client=client, request=DebugServerRequest(status=DebugServerRequest.Status())
    )
    commands = response.status.lldb_bootstrap_commands
    if not len(commands):
        return None
    return commands


async def daemon(
    client: CompanionClient, stream: Stream[DebugServerRequest, DebugServerResponse]
) -> None:
    async with client.stub.debugserver.open() as out_stream:
        await join_streams(stream, out_stream)


CLIENT_PROPERTIES = [  # pyre-ignore
    debugserver_start,
    debugserver_status,
    debugserver_stop,
]
