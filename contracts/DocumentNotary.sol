// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title DocumentNotary
/// @notice Immutable proof-of-existence for document hashes on Ethereum.
/// @dev Stores only SHA-256 hashes. Never stores document content.
contract DocumentNotary {
    struct Document {
        address submitter;
        uint256 timestamp;
        string description;
        bool exists;
    }

    mapping(bytes32 => Document) public documents;
    mapping(address => bytes32[]) public submitterDocuments;
    uint256 public totalDocuments;

    event DocumentNotarized(
        bytes32 indexed docHash,
        address indexed submitter,
        uint256 timestamp,
        string description
    );

    /// @notice Notarize a document hash
    function notarize(bytes32 docHash, string calldata description) external {
        require(docHash != bytes32(0), "Invalid hash");
        require(!documents[docHash].exists, "Already notarized");

        documents[docHash] = Document({
            submitter: msg.sender,
            timestamp: block.timestamp,
            description: description,
            exists: true
        });

        submitterDocuments[msg.sender].push(docHash);
        totalDocuments++;

        emit DocumentNotarized(docHash, msg.sender, block.timestamp, description);
    }

    /// @notice Check if a hash has been notarized (view, free)
    function verify(bytes32 docHash)
        external
        view
        returns (
            bool exists,
            address submitter,
            uint256 timestamp,
            string memory description
        )
    {
        Document memory doc = documents[docHash];
        return (doc.exists, doc.submitter, doc.timestamp, doc.description);
    }

    /// @notice Get full document record
    function getDocument(bytes32 docHash)
        external
        view
        returns (
            address submitter,
            uint256 timestamp,
            string memory description,
            bool exists
        )
    {
        Document memory doc = documents[docHash];
        return (doc.submitter, doc.timestamp, doc.description, doc.exists);
    }

    /// @notice Get all document hashes submitted by an address
    function getDocumentsBySubmitter(address submitter) external view returns (bytes32[] memory) {
        return submitterDocuments[submitter];
    }
}
