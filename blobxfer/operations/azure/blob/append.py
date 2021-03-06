# Copyright (c) Microsoft Corporation
#
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

# compat imports
from __future__ import absolute_import, division, print_function
from builtins import (  # noqa
    bytes, dict, int, list, object, range, ascii, chr, hex, input,
    next, oct, open, pow, round, super, filter, map, zip
)
# stdlib imports
import logging
# non-stdlib imports
import azure.storage.blob
# local imports
import blobxfer.retry

# create logger
logger = logging.getLogger(__name__)


def create_client(storage_account, timeout):
    # type: (blobxfer.operations.azure.StorageAccount,
    #        tuple) -> AppendBlobService
    """Create Append blob client
    :param blobxfer.operations.azure.StorageAccount storage_account:
        storage account
    :param tuple timeout: timeout tuple
    :rtype: AppendBlobService
    :return: append blob service client
    """
    if storage_account.is_sas:
        client = azure.storage.blob.AppendBlobService(
            account_name=storage_account.name,
            sas_token=storage_account.key,
            endpoint_suffix=storage_account.endpoint,
            request_session=storage_account.session,
            socket_timeout=timeout)
    else:
        client = azure.storage.blob.AppendBlobService(
            account_name=storage_account.name,
            account_key=storage_account.key,
            endpoint_suffix=storage_account.endpoint,
            request_session=storage_account.session,
            socket_timeout=timeout)
    # set retry policy
    client.retry = blobxfer.retry.ExponentialRetryWithMaxWait().retry
    return client


def create_blob(ase, timeout=None):
    # type: (blobxfer.models.azure.StorageEntity, int) -> None
    """Create append blob
    :param blobxfer.models.azure.StorageEntity ase: Azure StorageEntity
    :param int timeout: timeout
    """
    ase.client.create_blob(
        container_name=ase.container,
        blob_name=ase.name,
        content_settings=azure.storage.blob.models.ContentSettings(
            content_type=blobxfer.util.get_mime_type(ase.name)
        ),
        timeout=timeout)  # noqa


def append_block(ase, data, timeout=None):
    # type: (blobxfer.models.azure.StorageEntity, bytes, int) -> None
    """Appends a block into remote blob
    :param blobxfer.models.azure.StorageEntity ase: Azure StorageEntity
    :param bytes data: data
    :param int timeout: timeout
    """
    ase.client.append_block(
        container_name=ase.container,
        blob_name=ase.name,
        block=data,
        validate_content=False,  # integrity is enforced with HTTPS
        timeout=timeout)  # noqa
