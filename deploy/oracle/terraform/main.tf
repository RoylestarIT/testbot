provider "oci" {
  region              = var.region
  tenancy_ocid        = var.tenancy_ocid
  user_ocid           = var.user_ocid
  fingerprint         = var.fingerprint
  private_key_path    = var.private_key_path
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

data "oci_core_images" "ubuntu_arm" {
  compartment_id           = var.compartment_id
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "22.04"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_vcn" "reviewpilot" {
  compartment_id = var.compartment_id
  cidr_blocks    = ["10.42.0.0/16"]
  display_name   = "reviewpilot-vcn"
  dns_label      = "reviewpilot"
}

resource "oci_core_internet_gateway" "reviewpilot" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.reviewpilot.id
  display_name   = "reviewpilot-igw"
  enabled        = true
}

resource "oci_core_route_table" "reviewpilot" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.reviewpilot.id
  display_name   = "reviewpilot-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.reviewpilot.id
  }
}

resource "oci_core_security_list" "reviewpilot" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.reviewpilot.id
  display_name   = "reviewpilot-sl"

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

resource "oci_core_subnet" "reviewpilot" {
  compartment_id             = var.compartment_id
  vcn_id                     = oci_core_vcn.reviewpilot.id
  cidr_block                 = "10.42.1.0/24"
  display_name               = "reviewpilot-subnet"
  dns_label                  = "bot"
  prohibit_public_ip_on_vnic = false
  route_table_id             = oci_core_route_table.reviewpilot.id
  security_list_ids          = [oci_core_security_list.reviewpilot.id]
}

resource "oci_core_instance" "reviewpilot" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = var.instance_display_name
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = var.ocpus
    memory_in_gbs = var.memory_in_gbs
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_arm.images[0].id
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.reviewpilot.id
    assign_public_ip = true
    hostname_label   = "reviewpilot"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(templatefile("${path.module}/cloud-init.tpl", {
      git_ref = var.git_ref
    }))
  }
}
